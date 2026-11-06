import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix


class SearchEngine:
    """Moteur de recherche sur un Corpus : matrices Documents x Termes
    (TF et TF-IDF) et similarité cosinus."""

    COLONNES = ["id", "score", "type", "titre", "url"]

    def __init__(self, corpus):
        self.corpus = corpus
        # La matrice Documents x Termes est construite dès l'instanciation
        self.construire_matrices()

    def construire_matrices(self):
        """Construit vocab, mat_TF et mat_TFxIDF à partir du corpus."""
        documents = self.corpus.documents
        # La ligne i de la matrice correspond au document self.doc_ids[i]
        self.doc_ids = list(documents.keys())
        # On mémorise l'état du corpus pour détecter s'il change ensuite
        self._id_document_construit = self.corpus.id_document

        # Découpage de chaque document, une seule fois
        mots_par_doc = [self.corpus.mots_du_texte(documents[i].texte) for i in self.doc_ids]

        # Vocabulaire : mots uniques (set), triés, chacun avec son identifiant
        tous_les_mots = set()
        for mots in mots_par_doc:
            tous_les_mots.update(mots)
        self.vocab = {mot: {"id": j} for j, mot in enumerate(sorted(tous_les_mots))}

        # Matrice TF : on ne note que les cases non nulles (ligne, colonne, valeur)
        lignes, colonnes, valeurs = [], [], []
        for i, mots in enumerate(mots_par_doc):
            compte = {}  # mot -> nombre d'occurrences dans ce document
            for mot in mots:
                compte[mot] = compte.get(mot, 0) + 1
            for mot, nb in compte.items():
                lignes.append(i)
                colonnes.append(self.vocab[mot]["id"])
                valeurs.append(nb)
        self.mat_TF = csr_matrix((valeurs, (lignes, colonnes)),
                                 shape=(len(self.doc_ids), len(self.vocab)))

        # Totaux par mot, calculés à partir de la matrice (une colonne = un mot)
        nb_occurrences = np.asarray(self.mat_TF.sum(axis=0)).ravel()  # somme de la colonne
        nb_documents = self.mat_TF.getnnz(axis=0)  # cases non nulles de la colonne
        for mot, infos in self.vocab.items():
            j = infos["id"]
            infos["nb_occurrences"] = int(nb_occurrences[j])
            infos["nb_documents"] = int(nb_documents[j])

        # TF-IDF : idf = log(N / df), un mot présent partout pèse 0
        self.idf = np.log(len(self.doc_ids) / nb_documents)
        # multiply : chaque colonne j est multipliée par idf[j]
        self.mat_TFxIDF = csr_matrix(self.mat_TF.multiply(self.idf))
        self.mat_TFxIDF.eliminate_zeros()  # retire les 0 stockés (mots présents partout)

        # Norme de chaque document, calculée une fois pour toutes les recherches
        self.normes_docs = np.sqrt(
            np.asarray(self.mat_TFxIDF.multiply(self.mat_TFxIDF).sum(axis=1)).ravel())
        self.normes_docs[self.normes_docs == 0] = 1  # évite une division par zéro

    def search(self, mots_cles, n=5):
        """Renvoie un DataFrame des n documents les plus proches des mots-clés
        (similarité cosinus sur les vecteurs TF-IDF)."""
        # Des documents ont été ajoutés depuis la construction : on reconstruit
        if self.corpus.id_document != self._id_document_construit:
            self.construire_matrices()

        # 1. Mots-clés -> vecteur sur le vocabulaire (même nettoyage que les documents)
        vecteur = np.zeros(len(self.vocab))
        for mot in self.corpus.mots_du_texte(mots_cles):
            if mot in self.vocab:  # un mot inconnu du corpus ne peut rien apporter
                vecteur[self.vocab[mot]["id"]] += 1
        vecteur *= self.idf  # même pondération TF-IDF que les documents

        norme_requete = np.linalg.norm(vecteur)
        if norme_requete == 0:  # aucun mot utile dans la requête
            return pd.DataFrame(columns=self.COLONNES)

        # 2. Similarité cosinus = produit scalaire / (norme document x norme requête)
        produits = self.mat_TFxIDF @ vecteur  # un produit scalaire par document
        scores = produits / (self.normes_docs * norme_requete)

        # 3. Tri décroissant, on garde les n meilleurs documents de score > 0
        resultats = []
        for i in np.argsort(scores)[::-1][:n]:
            if scores[i] <= 0:
                break
            doc = self.corpus.documents[self.doc_ids[i]]
            resultats.append((self.doc_ids[i], round(scores[i], 3), doc.getType(), doc.titre, doc.url))
        return pd.DataFrame(resultats, columns=self.COLONNES)
