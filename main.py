# main.py

from CorpusSingleton import CorpusSingleton
from Corpus import Corpus
from DocumentFactory import DocumentFactory
import praw
import urllib.request, urllib.parse
import xmltodict
import os


# -------------------------------------------------------
# OPTION : si True → récupère depuis l'API Reddit & Arxiv
#           False → charge corpus.csv
# -------------------------------------------------------
RECUPERER_DEPUIS_API = False


# =======================================================
#     RÉCUPÉRATION DES DONNÉES REDDIT + ARXIV
# =======================================================
def recuperer_donnees():
    corpus = CorpusSingleton("AI Research")

    # -----------------------------
    # Récupération depuis Reddit
    # -----------------------------
    try:
        reddit = praw.Reddit(
            client_id="VOTRE_CLIENT_ID",
            client_secret="VOTRE_SECRET",
            user_agent="P_IA (by u/VOTRE_USER)"
        )

        theme = "artificial intelligence"

        for post in reddit.subreddit("all").search(theme, limit=10):
            texte = (post.title + " " + post.selftext).replace("\n", " ")
            auteur = str(post.author) if post.author else "Inconnu"

            doc = DocumentFactory.create_document(
                source="Reddit",
                titre=post.title,
                auteur_or_auteurs=auteur,
                date=post.created_utc,
                url=post.url,
                texte=texte,
                nb_commentaires=post.num_comments,
            )
            corpus.ajouter_document(doc)

    except Exception as e:
        print(f"Erreur Reddit : {e}")

    # -----------------------------
    # Récupération depuis Arxiv
    # -----------------------------
    try:
        theme_encoded = urllib.parse.quote("artificial intelligence")
        url = f"http://export.arxiv.org/api/query?search_query=all:{theme_encoded}&start=0&max_results=5"

        with urllib.request.urlopen(url) as response:
            data = response.read()

        feed = xmltodict.parse(data)
        entries = feed["feed"]["entry"]
        if isinstance(entries, dict):
            entries = [entries]

        for entry in entries:
            texte = entry["summary"].replace("\n", " ")

            authors = entry["author"]
            if isinstance(authors, dict):
                liste_auteurs = [authors["name"]]
            else:
                liste_auteurs = [a["name"] for a in authors]

            doc = DocumentFactory.create_document(
                source="Arxiv",
                titre=entry["title"],
                auteur_or_auteurs=liste_auteurs,
                date=entry["published"],
                url=entry["id"],
                texte=texte,
            )
            corpus.ajouter_document(doc)

    except Exception as e:
        print(f"Erreur Arxiv : {e}")

    return corpus


# =======================================================
#                  TESTS AUTOMATIQUES
# =======================================================
def tests(corpus):
    print("========== STATS BASIQUES ==========")
    corpus.afficher_stats_basiques()

    print("\n========== CONCAT TEXTE ==========")
    corpus.concatener_textes()

    print("\n========== TRI PAR TITRE ==========")
    corpus.afficher_par_titre(5)

    print("\n========== TRI PAR DATE ==========")
    corpus.afficher_par_date(5)

    print("\n========== STATS LEXICALES ==========")
    corpus.stats(20)

    print("\n========== CONCORDE ==========")
    df = corpus.concorde("intelligence", 25)
    print(df.head())

    print("\n========== SEARCH ==========")
    print(corpus.search("data"))


# =======================================================
#                         MAIN
# =======================================================
def main():
    if not os.path.exists("data"):
        os.makedirs("data")

    if RECUPERER_DEPUIS_API:
        corpus = recuperer_donnees()
        corpus.save("data/corpus.csv")
    else:
        if os.path.exists("data/corpus.csv"):
            corpus = CorpusSingleton("AI Research")
            temp = Corpus.load("data/corpus.csv")
            corpus.id2doc = temp.id2doc
            corpus.authors = temp.authors
            corpus.ndoc = temp.ndoc
            corpus.naut = temp.naut
        else:
            corpus = recuperer_donnees()
            corpus.save("data/corpus.csv")

    tests(corpus)
    print(f"\n📌 Résumé final : {corpus.ndoc} documents, {corpus.naut} auteurs")


if __name__ == "__main__":
    main()
