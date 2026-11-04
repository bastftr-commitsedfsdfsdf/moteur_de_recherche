from document import Document


class RedditDocument(Document):
    def __init__(self, titre, auteur, date, url, texte, nb_commentaires=0):
        # On laisse la classe mère initialiser les attributs communs
        super().__init__(titre, auteur, date, url, texte, type="reddit")
        self._nb_commentaires = nb_commentaires

    # Accesseur (getter) : permet de lire doc.nb_commentaires
    @property
    def nb_commentaires(self):
        return self._nb_commentaires

    # Mutateur (setter) : permet d'écrire doc.nb_commentaires = ...
    @nb_commentaires.setter
    def nb_commentaires(self, valeur):
        if valeur < 0:
            raise ValueError("Le nombre de commentaires ne peut pas être négatif")
        self._nb_commentaires = valeur

    def getType(self):
        return "reddit"

    def __str__(self):
        return f"[Reddit] {self.titre} ({self.nb_commentaires} commentaires)"
