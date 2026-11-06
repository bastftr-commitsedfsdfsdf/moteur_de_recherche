from Document import ArxivDocument, RedditDocument


class DocumentFactory:
    """Fabrique : renvoie la bonne classe fille selon la source."""

    @staticmethod
    def creer(type, titre, auteur, date, url, texte, **specifiques):
        # **specifiques : champs propres à une source (nb_commentaires, coauteurs)
        if type == "reddit":
            return RedditDocument(titre, auteur, date, url, texte, **specifiques)
        if type == "arxiv":
            return ArxivDocument(titre, auteur, date, url, texte, **specifiques)
        raise ValueError(f"Type de document inconnu : {type!r}")
