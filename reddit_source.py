import os
from datetime import datetime

import praw
from dotenv import load_dotenv

from document_factory import DocumentFactory


class RedditSource:
    """Récupère des posts Reddit via l'API (librairie praw)."""

    def __init__(self, subreddit, limit=10):
        self.subreddit = subreddit
        self.limit = limit

        # Les identifiants de l'API sont lus dans le fichier .env (non versionné)
        load_dotenv()
        self.reddit = praw.Reddit(
            client_id=os.getenv("ID_CLIENT"),
            client_secret=os.getenv("SECRET_CLIENT"),
            user_agent=os.getenv("USER_AGENT"),
        )

    def fetch(self):
        """Renvoie la liste des Document correspondant aux posts 'hot' du subreddit."""
        documents = []
        for post in self.reddit.subreddit(self.subreddit).hot(limit=self.limit):
            # Le titre est toujours présent, le contenu textuel est dans 'selftext'
            texte = post.title + ". " + post.selftext
            documents.append(DocumentFactory.creer(
                "reddit",
                titre=post.title,
                # post.author vaut None si le compte a été supprimé
                auteur=str(post.author) if post.author else "inconnu",
                # created_utc est un timestamp (secondes) -> objet datetime
                date=datetime.fromtimestamp(post.created_utc),
                url="https://www.reddit.com" + post.permalink,
                # On remplace les sauts de ligne par des espaces
                texte=texte.replace("\n", " ").strip(),
                nb_commentaires=post.num_comments,
            ))
        return documents


if __name__ == "__main__":
    # Petit test : affiche les documents récupérés
    for doc in RedditSource("Aerodynamics", limit=5).fetch():
        print("---")
        doc.afficher()
