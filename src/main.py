from CorpusSingleton import CorpusSingleton
from Corpus import Corpus
from DocumentFactory import DocumentFactory
import pandas as pd
import os


def charger_corpus():
    chemin = os.path.join("data", "corpus.csv")
    if not os.path.exists(chemin):
        raise FileNotFoundError(f"Fichier {chemin} introuvable.")

    print("\n Chargement corpus.csv…")
    df = pd.read_csv(chemin, sep="\t")
    corpus = Corpus.from_dataframe("Corpus chargé", df)
    print(f"📂 Corpus chargé : {corpus.ndoc} documents, {corpus.naut} auteurs\n")
    return corpus


# ======================
#   MENUS DE TEST
# ======================

def tests_td3(corpus: Corpus):
    print("\n===== 🔍 TESTS TD3 =====\n")
    stats = corpus.stats_documents()
    print(f"📊 Taille du corpus : {corpus.ndoc} documents\n")
    print("Statistiques par document :")
    print("-" * 80)
    print(f"{'ID':<5} {'Nb mots':<10} {'Nb phrases':<12} {'Nb caractères':<14}")
    print("-" * 80)
    for _, row in stats.iterrows():
        print(
            f"{int(row['id']):<5} {int(row['nb_mots']):<10} {int(row['nb_phrases']):<12} {int(row['nb_caracteres']):<14}"
        )
    _ = corpus.chaine_concatenee()
    print("Chaîne concaténée générée.\n")


def tests_td4(corpus: Corpus):
    print("\n===== 📘 TESTS TD4 =====")
    exemple = next(iter(corpus.id2doc.values()))
    print("Document exemple :")
    print(exemple)
    print(f"Titre : {exemple.titre}")
    print(f"Auteur : {exemple.auteur}")
    print(f"Date : {exemple.date}")
    print(f"URL : {exemple.url}")
    print(f"Texte : {(exemple.texte[:150] + '...') if exemple.texte else ''}")
    print(
        f"Type : {getattr(exemple, 'source', exemple.getType() if hasattr(exemple, 'getType') else 'Document')}\n"
    )

    print(f"Nombre d’auteurs : {corpus.naut}\n")

    print("🔠 Tri par titre :")
    for doc in corpus.trier_par_titre(5):
        print(doc)
    print("\n⏳ Tri par date :")
    for doc in corpus.trier_par_date(5):
        print(doc)

    print("\n💾 Test sauvegarde & rechargement...")
    chemin = os.path.join("data", "corpus_test.csv")
    corpus.save(chemin)
    df = pd.read_csv(chemin, sep="\t")
    corpus2 = Corpus.from_dataframe("Corpus rechargé", df)
    print(f"📂 Corpus chargé : {corpus2.ndoc} documents, {corpus2.naut} auteurs")
    print(corpus2)


def tests_td5(corpus: Corpus):
    from Document import RedditDocument, ArxivDocument

    print("\n===== 🧬 TESTS TD5 =====")
    print("Exemples documents :")
    i = 0
    for doc in corpus.id2doc.values():
        if isinstance(doc, RedditDocument):
            print(doc)
            print(f"Commentaires : {getattr(doc, 'nb_commentaires', '?')}")
            i += 1
        if i >= 5:
            break

    print("\n🧪 Test Singleton :")
    c1 = CorpusSingleton("corpus A")
    c2 = CorpusSingleton("corpus B")
    print("Singleton OK ?", c1 is c2)

    print("\n🧪 Test Factory :")
    doc = DocumentFactory.create_document(
        source="Reddit",
        titre="Test",
        auteur_or_auteurs="Moi",
        date="2024-01-01",
        url="https://exemple.org",
        texte="Ceci est un document de test.",
        nb_commentaires=2,
    )
    print("Document via Factory :", doc)


def tests_td6(corpus: Corpus):
    print("\n===== 🧠 TESTS TD6 =====\n")
    motif = "intelligence"
    print(f"🔍 SEARCH '{motif}' :")
    matches = corpus.search_regex(motif)
    print(f"{len(matches)} occurrences trouvées\n")

    print(f"📑 CONCORDE '{motif}' :")
    concorde_df = corpus.concorde(motif)
    print(concorde_df.head(), "\n")

    print("📊 STATISTIQUES TF/DF :\n")
    table = corpus.construire_vocabulaire()
    print(f"📊 Nombre total de mots distincts : {len(table)}")
    print("🔝 Top 20 mots les plus fréquents :\n")
    print(table.head(20))
    print()


def tests_td7(corpus: Corpus):
    print("\n===== 🔎 TESTS TD7 : MOTEUR DE RECHERCHE =====\n")
    while True:
        requete = input("🔍 Entrez votre requête (ou vide pour revenir au menu) : ").strip()
        if not requete:
            break
        k_str = input("Combien de documents afficher ? (défaut 5) : ").strip()
        try:
            k = int(k_str) if k_str else 5
        except ValueError:
            k = 5

        resultats = corpus.search_advanced(requete, k=k)
        if resultats.empty:
            print("Aucun document trouvé.\n")
            continue

        print("\nRésultats :\n")
        for _, row in resultats.iterrows():
            print(f"- [score={row['score']}] (doc {row['id']}) {row['titre']} – {row['auteur']}")
            print(f"  {row['extrait']}\n")


def menu(corpus: Corpus):
    while True:
        print("\n========== MENU ==========")
        print("1. Tests TD3")
        print("2. Tests TD4")
        print("3. Tests TD5")
        print("4. Tests TD6 (search / concorde / stats)")
        print("5. Tests TD7 (moteur de recherche)")
        print("0. Quitter")
        choix = input("> ").strip()

        if choix == "1":
            tests_td3(corpus)
        elif choix == "2":
            tests_td4(corpus)
        elif choix == "3":
            tests_td5(corpus)
        elif choix == "4":
            tests_td6(corpus)
        elif choix == "5":
            tests_td7(corpus)
        elif choix == "0":
            break
        else:
            print("Choix invalide.")


def main():
    corpus = charger_corpus()
    menu(corpus)
    print("\nFin du programme.")


if __name__ == "__main__":
    main()
