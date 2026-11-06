import re
from datetime import datetime

import pandas as pd

from Author import Author
from document_factory import DocumentFactory


class Corpus:
    # Singleton : l'unique instance est stockée ici
    _instance = None

    def __new__(cls, nom="Corpus"):
        # __new__ crée l'objet : on ne le fait qu'au premier appel
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.nom = nom
            cls._instance.documents = {}   # id -> Document
            cls._instance.id_document = 0  # prochain identifiant à attribuer
            cls._instance.authors = {}     # nom -> Author
            cls._instance._all_text = None  # texte concaténé, construit à la demande
        return cls._instance

    def add(self, doc):
        """Ajoute un document au corpus et met à jour les auteurs."""
        id_doc = self.id_document
        self.documents[id_doc] = doc
        self.id_document += 1
        # Le corpus a changé : la chaîne concaténée n'est plus à jour
        self._all_text = None

        # Chaque classe de document sait lister ses auteurs (principal + coauteurs)
        for name in doc.tous_les_auteurs():
            if name not in self.authors:
                self.authors[name] = Author(name)
            self.authors[name].add(id_doc, doc)

    def _get_all_text(self):
        """Chaîne unique de tous les textes, construite une seule fois."""
        if self._all_text is None:
            # "\n" entre les documents : un passage ne peut pas en enjamber deux
            self._all_text = "\n".join(doc.texte for doc in self.documents.values())
        return self._all_text

    def search(self, motcle, contexte=40):
        """Renvoie les passages contenant le mot-clé, avec `contexte`
        caractères de part et d'autre (même ligne, donc même document)."""
        # re.escape : les caractères spéciaux du mot-clé sont lus littéralement
        # \b : le mot doit être entier (pas "car" dans "carbon")
        motif = rf".{{0,{contexte}}}\b{re.escape(motcle)}\b.{{0,{contexte}}}"
        return [m.group() for m in re.finditer(motif, self._get_all_text(), re.IGNORECASE)]

    def concorde(self, expression, taille_contexte=30):
        """Concordancier : tableau (contexte gauche, motif trouvé, contexte droit)
        pour chaque occurrence de l'expression (expression régulière)."""
        texte = self._get_all_text()
        lignes = []
        for m in re.finditer(expression, texte, re.IGNORECASE):
            # Contexte gauche : taille_contexte caractères avant le motif...
            gauche = texte[max(0, m.start() - taille_contexte):m.start()]
            # ...et droit : après. On coupe au saut de ligne le plus proche
            # pour ne pas déborder sur un autre document.
            droite = texte[m.end():m.end() + taille_contexte]
            gauche = gauche.split("\n")[-1]
            droite = droite.split("\n")[0]
            lignes.append((gauche, m.group(), droite))
        return pd.DataFrame(lignes, columns=["contexte gauche", "motif trouvé", "contexte droit"])

    @staticmethod
    def nettoyer_texte(texte):
        """Minuscules, sans sauts de ligne, ni ponctuation, ni chiffres."""
        texte = texte.lower()
        texte = texte.replace("\n", " ")
        # [\W\d_] : tout ce qui n'est pas une lettre (ponctuation, chiffres, _)
        texte = re.sub(r"[\W\d_]+", " ", texte)
        return texte.strip()

    def mots_du_texte(self, texte):
        """Découpe un texte nettoyé en liste de mots."""
        # Délimiteurs : espaces, tabulations et ponctuation courante de l'anglais
        mots = re.split(r"[\s.,;:!?'\"()\[\]-]+", self.nettoyer_texte(texte))
        return [mot for mot in mots if mot]  # retire les chaînes vides

    def construire_freq(self):
        """Construit le vocabulaire et le tableau freq en un seul parcours."""
        # Vocabulaire : ses clés sont les mots (uniques par nature),
        # sa valeur le nombre total d'apparitions (term frequency)
        nb_occurrences = {}
        nb_documents = {}  # mot -> nombre de documents qui le contiennent (document frequency)

        for doc in self.documents.values():
            mots = self.mots_du_texte(doc.texte)
            for mot in mots:
                nb_occurrences[mot] = nb_occurrences.get(mot, 0) + 1
            # set(mots) : chaque mot compte une seule fois par document
            for mot in set(mots):
                nb_documents[mot] = nb_documents.get(mot, 0) + 1

        self.freq = pd.DataFrame({
            "term frequency": pd.Series(nb_occurrences),
            "document frequency": pd.Series(nb_documents),
        }).sort_values("term frequency", ascending=False)
        return self.freq

    def stats(self, n=10):
        """Affiche le nombre de mots différents et les n plus fréquents."""
        freq = self.construire_freq()
        print(f"Nombre de mots différents : {len(freq)}")
        print(f"Les {n} mots les plus fréquents :")
        print(freq.head(n).to_string())

    def afficher_par_date(self, n):
        """Affiche les n premiers documents, du plus ancien au plus récent."""
        docs = sorted(self.documents.values(), key=lambda d: d.date)
        for doc in docs[:n]:
            print(f"{doc.date:%Y-%m-%d} - {doc}")

    def afficher_par_titre(self, n):
        """Affiche les n premiers documents, par ordre alphabétique du titre."""
        docs = sorted(self.documents.values(), key=lambda d: d.titre.lower())
        for doc in docs[:n]:
            print(doc)

    def afficher_avec_source(self):
        """Affiche tous les documents avec leur source (Reddit ou Arxiv)."""
        for id_doc, doc in self.documents.items():
            print(f"{id_doc:>3} [{doc.getType()}] {doc.titre}")

    def save(self, path):
        """Enregistre le corpus dans un CSV (séparateur tabulation)."""
        docs = list(self.documents.values())
        df = pd.DataFrame({
            "id": list(self.documents.keys()),
            "titre": [d.titre for d in docs],
            "auteur": [d.auteur for d in docs],
            "date": [d.date.isoformat() for d in docs],
            "url": [d.url for d in docs],
            "texte": [d.texte for d in docs],
            "type": [d.getType() for d in docs],
            # Champ propre aux documents Reddit, vide pour les autres sources
            "nb_commentaires": [getattr(d, "nb_commentaires", "") for d in docs],
            # Champ propre aux documents Arxiv, noms séparés par ", "
            "coauteurs": [", ".join(getattr(d, "coauteurs", [])) for d in docs],
        })
        df.to_csv(path, sep="\t", index=False)

    def load(self, path):
        """Vide le corpus puis le reconstruit à partir d'un CSV."""
        self.documents = {}
        self.id_document = 0
        self.authors = {}
        self._all_text = None

        # fillna("") : une cellule vide ne doit pas devenir NaN
        df = pd.read_csv(path, sep="\t").fillna("")
        for row in df.itertuples():
            # Champs propres à chaque source
            if row.type == "reddit":
                specifiques = {"nb_commentaires": int(row.nb_commentaires)}
            else:
                specifiques = {"coauteurs": row.coauteurs.split(", ") if row.coauteurs else []}

            # La fabrique choisit la bonne classe de document
            self.add(DocumentFactory.creer(
                row.type,
                titre=row.titre,
                auteur=row.auteur,
                date=datetime.fromisoformat(row.date),
                url=row.url,
                texte=row.texte,
                **specifiques,
            ))

    def __repr__(self):
        return (f"Corpus '{self.nom}' : {len(self.documents)} documents, "
                f"{len(self.authors)} auteurs")
