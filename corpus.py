from datetime import datetime

import pandas as pd

from author import Author
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
        return cls._instance

    def add(self, doc):
        """Ajoute un document au corpus et met à jour les auteurs."""
        id_doc = self.id_document
        self.documents[id_doc] = doc
        self.id_document += 1

        # Chaque classe de document sait lister ses auteurs (principal + coauteurs)
        for name in doc.tous_les_auteurs():
            if name not in self.authors:
                self.authors[name] = Author(name)
            self.authors[name].add(id_doc, doc)

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
        df = pd.DataFrame({
            "id": list(self.documents.keys()),
            "titre": [d.titre for d in self.documents.values()],
            "auteur": [d.auteur for d in self.documents.values()],
            "date": [d.date.isoformat() for d in self.documents.values()],
            "url": [d.url for d in self.documents.values()],
            "texte": [d.texte for d in self.documents.values()],
            "type": [d.getType() for d in self.documents.values()],
            # Champ propre aux documents Reddit, vide pour les autres sources
            "nb_commentaires": [getattr(d, "nb_commentaires", "")
                                for d in self.documents.values()],
            # Champ propre aux documents Arxiv, noms séparés par ", "
            "coauteurs": [", ".join(getattr(d, "coauteurs", []))
                          for d in self.documents.values()],
        })
        df.to_csv(path, sep="\t", index=False)

    def load(self, path):
        """Vide le corpus puis le reconstruit à partir d'un CSV."""
        self.documents = {}
        self.id_document = 0
        self.authors = {}

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
