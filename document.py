class Document:
    def __init__(self, titre, auteur, date, url, texte, type=""):
        self.type = type  # source du document : 'reddit' ou 'arxiv'
        self.titre = titre
        self.auteur = auteur
        self.date = date
        self.url = url
        self.texte = texte

    def getType(self):
        """Type du document ; les classes filles le redéfinissent."""
        return self.type

    def tous_les_auteurs(self):
        """Liste de tous les auteurs du document (un seul ici)."""
        return [self.auteur]

    def afficher(self):
        print(f"Titre  : {self.titre}")
        print(f"Auteur : {self.auteur}")
        print(f"Date   : {self.date}")
        print(f"URL    : {self.url}")
        print(f"Texte  : {self.texte}")

    def __str__(self):
        return self.titre
