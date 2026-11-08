import os

import numpy as np

from arxiv_source import ArxivSource
from Corpus import Corpus
from reddit_source import RedditSource
from search_engine import SearchEngine

CSV_PATH = "corpus.csv"
NB_DOCS = 1000
LONGUEUR_MIN = 100  # les documents plus courts (en caractères) sont écartés


def fetch_documents():
    """Interroge les deux API et renvoie la liste des Document."""
    docs = []
    docs += RedditSource("Aerodynamics", limit=NB_DOCS).fetch()
    docs += ArxivSource("vehicle aerodynamics", limit=NB_DOCS).fetch()
    return docs


def stats_auteur(authors):
    """Demande un nom d'auteur et affiche ses statistiques."""
    name = input("Nom de l'auteur : ").strip()
    if name not in authors:
        print(f"Auteur '{name}' introuvable.")
        return
    author = authors[name]
    print(f"Nombre de documents : {author.nb_docs}")
    print(f"Taille moyenne des documents : {author.taille_moyenne():.1f} mots")


def afficher_top(moteur, matrice, n=10):
    """Affiche les n cases (document, mot) de plus haut score de la matrice."""
    mots = list(moteur.vocab)  # mots[j] = mot de la colonne j (vocab est trié)
    cases = matrice.tocoo()    # format (ligne, colonne, valeur) des cases non nulles
    # argsort trie les indices par score croissant ; [::-1] inverse ; [:n] garde les n premiers
    for k in np.argsort(cases.data)[::-1][:n]:
        id_doc = moteur.doc_ids[cases.row[k]]
        doc = moteur.corpus.documents[id_doc]
        print(f"{cases.data[k]:8.2f}  {mots[cases.col[k]]:<15} doc {id_doc:>2} : {doc.titre[:50]}")


if __name__ == "__main__":
    corpus = Corpus("Aerodynamique")

    # On n'interroge les API que si le fichier n'existe pas encore
    if os.path.exists(CSV_PATH):
        print(f"Chargement depuis {CSV_PATH}")
        corpus.load(CSV_PATH)
    else:
        print("Interrogation des API Reddit et Arxiv...")
        docs = fetch_documents()
        for doc in docs:
            if len(doc.texte) >= LONGUEUR_MIN:
                corpus.add(doc)
        print(f"{len(docs) - len(corpus.documents)} documents trop courts écartés")
        corpus.save(CSV_PATH)

    print(corpus)

    print("\nListe des documents avec leur source :")
    corpus.afficher_avec_source()

    print("\n5 premiers documents par date :")
    corpus.afficher_par_date(5)
    print("\n5 premiers documents par titre :")
    corpus.afficher_par_titre(5)

    # pour chaque document, nombre de mots (séparés par des espaces)
    # et de phrases (séparées par des points), comme demandé par l'énoncé
    for id_doc, doc in corpus.documents.items():
        nb_mots = len(doc.texte.split())
        nb_phrases = len([p for p in doc.texte.split(".") if p.strip()])
        print(f"Document {id_doc} : {nb_mots} mots, {nb_phrases} phrases")

    # recherche d'un mot-clé dans tout le corpus (expressions régulières)
    passages = corpus.search("aerodynamic")
    print(f"\n{len(passages)} passages contenant 'aerodynamic' :")
    for passage in passages[:5]:
        print(f"...{passage}...")

    # concordancier : le motif au centre, son contexte de chaque côté
    concordancier = corpus.concorde("aerodynamic", taille_contexte=30)
    print(f"\nConcordancier ({len(concordancier)} occurrences) :")
    print(concordancier.head(5).to_string())

    print("\nStatistiques du corpus :")
    corpus.stats(10)

    # moteur de recherche : les matrices Documents x Termes sont construites ici
    moteur = SearchEngine(corpus)
    print(f"\nmat_TF : {moteur.mat_TF.shape[0]} documents x {moteur.mat_TF.shape[1]} mots, "
          f"{moteur.mat_TF.nnz} cases non nulles")
    print("vocab['aerodynamic'] :", moteur.vocab.get("aerodynamic"))
    print("\n10 meilleurs scores de mat_TF :")
    afficher_top(moteur, moteur.mat_TF, 10)
    print("\n10 meilleurs scores de mat_TFxIDF :")
    afficher_top(moteur, moteur.mat_TFxIDF, 10)

    stats_auteur(corpus.authors)

    # recherche : on boucle jusqu'à une requête vide
    while True:
        requete = input("\nMots-clés (Entrée vide pour quitter) : ").strip()
        if not requete:
            break
        resultats = moteur.search(requete, 5)
        if resultats.empty:
            print("Aucun document trouvé.")
        else:
            print(resultats[["score", "type", "titre"]].to_string(index=False))
