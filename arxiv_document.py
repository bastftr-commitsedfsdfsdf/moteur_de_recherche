from document import Document


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
