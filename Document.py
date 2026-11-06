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


class ArxivDocument(Document):
    def __init__(self, titre, auteur, date, url, texte, coauteurs=None):
        # 'auteur' est l'auteur principal (le premier cité sur l'article)
        super().__init__(titre, auteur, date, url, texte, type="arxiv")
        # On évite une liste par défaut partagée entre instances : None -> []
        self._coauteurs = list(coauteurs) if coauteurs else []

    # Accesseur (getter) : doc.coauteurs
    @property
    def coauteurs(self):
        return self._coauteurs

    # Mutateur (setter) : doc.coauteurs = [...]
    @coauteurs.setter
    def coauteurs(self, valeur):
        if not isinstance(valeur, list):
            raise TypeError("coauteurs doit être une liste de noms")
        self._coauteurs = valeur

    def ajouter_coauteur(self, nom):
        """Ajoute un coauteur s'il n'est pas déjà dans la liste."""
        if nom not in self._coauteurs:
            self._coauteurs.append(nom)

    def tous_les_auteurs(self):
        """Auteur principal + coauteurs (redéfinit la méthode de Document)."""
        return [self.auteur] + self._coauteurs

    def getType(self):
        return "arxiv"

    def __str__(self):
        return (f"[Arxiv] {self.titre} - {self.auteur} "
                f"et {len(self._coauteurs)} coauteur(s)")
