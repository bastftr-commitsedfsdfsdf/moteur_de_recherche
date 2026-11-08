"""Backend Flask du moteur de recherche (Partie 3, version v3).
Lancement : python app.py, puis ouvrir http://localhost:5000"""
import os
from datetime import date

from flask import Flask, jsonify, render_template, request

from Corpus import Corpus
from main import CSV_PATH, LONGUEUR_MIN, fetch_documents
from search_engine import SearchEngine


def charger_corpus():
    """Charge le corpus depuis le CSV ; n'interroge les API que s'il n'existe pas."""
    corpus = Corpus("Aerodynamique")
    if os.path.exists(CSV_PATH):
        print(f"Chargement depuis {CSV_PATH}")
        corpus.load(CSV_PATH)
    else:
        print("Interrogation des API Reddit et Arxiv...")
        for doc in fetch_documents():
            if len(doc.texte) >= LONGUEUR_MIN:
                corpus.add(doc)
        corpus.save(CSV_PATH)
    return corpus


# Le corpus et le moteur sont construits une seule fois, au démarrage du serveur
corpus = charger_corpus()
moteur = SearchEngine(corpus)
print(corpus)

app = Flask(__name__)


def lire_date(texte):
    """Convertit "2024-01-31" en objet date ; renvoie None si vide ou invalide."""
    try:
        return date.fromisoformat(texte)
    except ValueError:
        return None


def garder(doc, source, auteur, debut, fin):
    """True si le document passe tous les filtres. Un filtre vide est ignoré."""
    if source and doc.getType() != source:
        return False
    # tous_les_auteurs : l'auteur principal + les coauteurs (Arxiv), polymorphisme
    if auteur and not any(auteur.lower() in nom.lower() for nom in doc.tous_les_auteurs()):
        return False
    if debut and doc.date.date() < debut:
        return False
    if fin and doc.date.date() > fin:
        return False
    return True


@app.route("/")
def accueil():
    """Page d'accueil : renvoie l'interface HTML (dossier templates/)."""
    dates = [doc.date.date() for doc in corpus.documents.values()]
    return render_template("index.html", nom=corpus.nom, nb_docs=len(corpus.documents),
                           auteurs=sorted(corpus.authors),  # pour les suggestions du champ auteur
                           date_min=min(dates).isoformat(), date_max=max(dates).isoformat())


@app.route("/api/search")
def api_search():
    """Recherche : /api/search?q=...&n=5&source=arxiv&auteur=...&debut=...&fin=...
    -> liste JSON des n meilleurs documents qui passent les filtres."""
    mots_cles = request.args.get("q", "")
    n = max(request.args.get("n", 5, type=int), 1)  # au moins 1 document
    source = request.args.get("source", "")
    auteur = request.args.get("auteur", "").strip()
    debut = lire_date(request.args.get("debut", ""))
    fin = lire_date(request.args.get("fin", ""))

    # On demande au moteur TOUS les documents pertinents (triés par score),
    # puis on garde les n premiers qui passent les filtres
    resultats = moteur.search(mots_cles, len(corpus.documents))
    documents = []
    for ligne in resultats.itertuples():
        doc = corpus.documents[ligne.id]
        if garder(doc, source, auteur, debut, fin):
            documents.append({
                "score": float(ligne.score),
                "type": ligne.type,
                "titre": ligne.titre,
                "url": ligne.url,
                "auteurs": ", ".join(doc.tous_les_auteurs()),
                "date": doc.date.strftime("%d/%m/%Y"),
            })
            if len(documents) == n:
                break
    return jsonify(documents)


if __name__ == "__main__":
    # host="0.0.0.0" : accepte les connexions venant de l'extérieur du conteneur Docker
    app.run(host="0.0.0.0", port=5000)
