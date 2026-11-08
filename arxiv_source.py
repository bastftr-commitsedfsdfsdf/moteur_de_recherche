import urllib.parse
import urllib.request
from datetime import datetime

import xmltodict

from document_factory import DocumentFactory


class ArxivSource:
    """Récupère des articles Arxiv via l'API (urllib + xmltodict)."""

    BASE_URL = "http://export.arxiv.org/api/query"

    def __init__(self, query, limit=1000):
        self.query = query
        self.limit = limit

    def fetch(self):
        """Renvoie la liste des ArxivDocument correspondant aux articles trouvés."""
        params = urllib.parse.urlencode({
            "search_query": "all:" + self.query,
            "start": 0,
            "max_results": self.limit,
        })
        req = urllib.request.Request(self.BASE_URL + "?" + params,
                                     headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req) as response:
            xml_data = response.read().decode("utf-8")

        entries = xmltodict.parse(xml_data)["feed"].get("entry", [])
        # S'il n'y a qu'un seul article, xmltodict renvoie un dict et pas une liste
        if isinstance(entries, dict):
            entries = [entries]

        documents = []
        for entry in entries:
            # 'author' est un dict s'il y a un seul auteur, une liste sinon
            auteurs = entry["author"]
            if isinstance(auteurs, dict):
                auteurs = [auteurs]
            noms = [a["name"] for a in auteurs]

            documents.append(DocumentFactory.creer(
                "arxiv",
                titre=entry["title"].replace("\n", " ").strip(),
                auteur=noms[0],  # auteur principal
                coauteurs=noms[1:],
                # ex : "2024-01-31T12:00:00Z" -> objet datetime
                date=datetime.strptime(entry["published"], "%Y-%m-%dT%H:%M:%SZ"),
                url=entry["id"],
                # Le contenu textuel d'un article est son résumé
                texte=entry["summary"].replace("\n", " ").strip(),
            ))
        return documents


if __name__ == "__main__":
    # Petit test : affiche les documents récupérés
    for doc in ArxivSource("vehicle aerodynamics", limit=5).fetch():
        print("---")
        doc.afficher()
