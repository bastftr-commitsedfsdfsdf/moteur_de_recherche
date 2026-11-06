class Author:
    def __init__(self, name):
        self.name = name
        self.nb_docs = 0
        self.production = {}  # id du document -> instance de Document

    def add(self, id_doc, doc):
        """Ajoute un document à la production de l'auteur."""
        self.production[id_doc] = doc
        self.nb_docs = len(self.production)

    def taille_moyenne(self):
        """Taille moyenne (en mots) des documents de l'auteur."""
        if self.nb_docs == 0:
            return 0
        total = sum(len(doc.texte.split()) for doc in self.production.values())
        return total / self.nb_docs

    def __str__(self):
        titres = ", ".join(doc.titre for doc in self.production.values())
        return f"{self.name} ({self.nb_docs} document(s)) : {titres}"
