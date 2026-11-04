import os

from arxiv_source import ArxivSource
from corpus import Corpus
from reddit_source import RedditSource

CSV_PATH = "corpus.csv"
NB_DOCS = 10
LONGUEUR_MIN = 100  # les documents plus courts (en caractères) sont écartés


def fetch_documents():
    """Interroge les deux API et renvoie la liste des Document."""
    docs = []
    docs += RedditSource("Aerodynamics", limit=NB_DOCS).fetch()
    docs += ArxivSource("vehicle aerodynamics", limit=NB_DOCS).fetch()
    return docs


def stats_auteur(authors):
    """Demande un nom d'auteur et affiche ses statistiques."""
    name = input("Nom de l'auteur : ").strip()
    if name not in authors:
        print(f"Auteur '{name}' introuvable.")
        return
    author = authors[name]
    print(f"Nombre de documents : {author.nb_docs}")
    print(f"Taille moyenne des documents : {author.taille_moyenne():.1f} mots")


if __name__ == "__main__":
    corpus = Corpus("Aerodynamique")

    # On n'interroge les API que si le fichier n'existe pas encore
    if os.path.exists(CSV_PATH):
        print(f"Chargement depuis {CSV_PATH}")
        corpus.load(CSV_PATH)
    else:
        print("Interrogation des API Reddit et Arxiv...")
        docs = fetch_documents()
        for doc in docs:
            if len(doc.texte) >= LONGUEUR_MIN:
                corpus.add(doc)
        print(f"{len(docs) - len(corpus.documents)} documents trop courts écartés")
        corpus.save(CSV_PATH)

    print(corpus)

    print("\nListe des documents avec leur source :")
    corpus.afficher_avec_source()

    print("\n5 premiers documents par date :")
    corpus.afficher_par_date(5)
    print("\n5 premiers documents par titre :")
    corpus.afficher_par_titre(5)

    # pour chaque document, nombre de mots et de phrases
    for id_doc, doc in corpus.documents.items():
        nb_mots = len(doc.texte.split())
        nb_phrases = doc.texte.count(".") + doc.texte.count("!") + doc.texte.count("?")
        print(f"Document {id_doc} : {nb_mots} mots, {nb_phrases} phrases")

    # unique chaîne de caractères de tous les documents
    all_text = " ".join(doc.texte for doc in corpus.documents.values())

    stats_auteur(corpus.authors)
