from Document import Document, RedditDocument, ArxivDocument
from Author import Author
import pandas as pd
from datetime import datetime
import re


class Corpus:
    def __init__(self, nom):
        self.nom = nom
        self.id2doc = {}
        self.authors = {}
        self.ndoc = 0
        self.naut = 0

        # Cache pour ne construire qu'une seule fois
        self._texte_concatene = None

    # =====================================================================
    #                          AJOUT DOCUMENTS
    # =====================================================================
    def ajouter_document(self, doc):
        """Ajoute un document au corpus"""
        doc_id = self.ndoc
        self.id2doc[doc_id] = doc
        self.ndoc += 1

        # Gestion des auteurs
        if doc.getType() == "Arxiv":
            auteurs = doc.auteurs
        else:
            auteurs = [doc.auteur]

        for auteur in auteurs:
            if auteur not in self.authors:
                self.authors[auteur] = Author(auteur)
                self.naut += 1
            self.authors[auteur].add(doc)

    # =====================================================================
    #                              TRI
    # =====================================================================
    def afficher_par_titre(self, n=None):
        docs_tries = sorted(self.id2doc.values(), key=lambda d: d.titre.lower())
        if n:
            docs_tries = docs_tries[:n]
        for doc in docs_tries:
            print(doc)

    def afficher_par_date(self, n=None):
        def get_date_sortable(doc):
            if isinstance(doc.date, (int, float)):
                return doc.date
            elif isinstance(doc.date, str):
                try:
                    dt = datetime.fromisoformat(doc.date.replace('Z', '+00:00'))
                    return dt.timestamp()
                except:
                    return 0
            return 0

        docs_tries = sorted(self.id2doc.values(), key=get_date_sortable, reverse=True)
        if n:
            docs_tries = docs_tries[:n]
        for doc in docs_tries:
            print(doc)

    # =====================================================================
    #                 STATISTIQUES AUTEURS (déjà existant)
    # =====================================================================
    def statistiques_auteur(self, nom_auteur):
        if nom_auteur not in self.authors:
            print(f"Auteur '{nom_auteur}' non trouvé dans le corpus.")
            return

        auteur = self.authors[nom_auteur]
        nb_docs = auteur.ndoc
        tailles = [len(doc.texte) for doc in auteur.production.values()]
        taille_moyenne = sum(tailles) / nb_docs if nb_docs > 0 else 0

        print(f"\n📊 Statistiques pour {nom_auteur}:")
        print(f"   - Nombre de documents produits : {nb_docs}")
        print(f"   - Taille moyenne des documents : {taille_moyenne:.2f} caractères")

    # =====================================================================
    #                 STATS BASIQUES (TD3)
    # =====================================================================
    def afficher_stats_basiques(self):
        print(f"\n📊 Taille du corpus : {self.ndoc} documents\n")

        print("Statistiques par document :")
        print("-" * 70)
        print(f"{'ID':<5} {'Nb mots':<10} {'Nb phrases':<12} {'Nb caractères':<15}")
        print("-" * 70)

        for doc_id, doc in self.id2doc.items():
            nb_mots = len(doc.texte.split())
            nb_phrases = doc.texte.count('.') + doc.texte.count('!') + doc.texte.count('?')
            nb_chars = len(doc.texte)
            print(f"{doc_id:<5} {nb_mots:<10} {nb_phrases:<12} {nb_chars:<15}")

    # =====================================================================
    #                 CONCATÉNATION DES TEXTES
    # =====================================================================
    def get_texte_concatene(self):
        """Construit la concaténation une seule fois (cache)."""
        if self._texte_concatene is None:
            self._texte_concatene = " ".join(doc.texte for doc in self.id2doc.values())
        return self._texte_concatene

    def concatener_textes(self):
        texte = self.get_texte_concatene()
        print(f"\n📝 Chaîne unique créée :")
        print(f"   - Longueur totale : {len(texte)} caractères")
        print(f"   - Nombre de mots : {len(texte.split())}")
        print(f"   - Extrait : {texte[:150]}...")
        return texte

    # =====================================================================
    #                   PARTIE 1 : EXPRESSIONS RÉGULIÈRES
    # =====================================================================
    def search(self, mot_clef):
        """Retourne les occurrences du mot clé dans le corpus."""
        texte = self.get_texte_concatene()

        motif = r"\b" + re.escape(mot_clef) + r"\b"
        occurrences = re.findall(motif, texte, flags=re.IGNORECASE)
        return occurrences

    def concorde(self, expression, contexte=30):
        """Concordancier sur l’expression donnée."""
        texte = self.get_texte_concatene()
        motif = re.compile(expression, re.IGNORECASE)

        lignes = []
        for m in motif.finditer(texte):
            deb, fin = m.span()
            gauche = texte[max(0, deb - contexte):deb]
            milieu = m.group()
            droite = texte[fin:fin + contexte]
            lignes.append([gauche, milieu, droite])

        return pd.DataFrame(lignes, columns=['contexte gauche', 'motif trouvé', 'contexte droit'])

    # =====================================================================
    #                   PARTIE 2 : STATISTIQUES LEXICALES
    # =====================================================================
    def nettoyer_texte(self, texte):
        texte = texte.lower()
        texte = texte.replace("\n", " ")
        texte = re.sub(r"[0-9]", " ", texte)
        texte = re.sub(r"[^\w\s]", " ", texte)
        texte = re.sub(r"\s+", " ", texte)
        return texte.strip()

    def construire_vocabulaire(self):
        vocab = {}

        for doc in self.id2doc.values():
            propre = self.nettoyer_texte(doc.texte)
            mots = propre.split()

            for m in mots:
                vocab[m] = vocab.get(m, 0) + 1

        return vocab

    def stats(self, n=20):
        """Affiche les stats textuelles : vocabulaire, TF, DF."""
        vocab_freq = self.construire_vocabulaire()

        # Document Frequency
        doc_freq = {mot: 0 for mot in vocab_freq}
        for doc in self.id2doc.values():
            uniques = set(self.nettoyer_texte(doc.texte).split())
            for m in uniques:
                doc_freq[m] += 1

        df = pd.DataFrame({
            "mot": list(vocab_freq.keys()),
            "term_frequency": list(vocab_freq.values()),
            "document_frequency": [doc_freq[m] for m in vocab_freq]
        }).sort_values(by="term_frequency", ascending=False)

        print(f"\n📊 Nombre de mots différents : {len(df)}")
        print(f"\n🔝 Top {n} mots les plus fréquents :")
        print(df.head(n))

        return df

    # =====================================================================
    #                       SAUVEGARDE / CHARGEMENT
    # =====================================================================
    def save(self, fichier="data/corpus.csv"):
        data = []
        for doc_id, doc in self.id2doc.items():
            data.append({
                "id": doc_id,
                "titre": doc.titre,
                "auteur": doc.auteur,
                "date": doc.date,
                "url": doc.url,
                "texte": doc.texte,
                "type": doc.getType(),
                "nb_commentaires": doc.nb_commentaires if isinstance(doc, RedditDocument) else None,
                "co_auteurs": ", ".join(doc.auteurs) if isinstance(doc, ArxivDocument) else None
            })

        df = pd.DataFrame(data)
        df.to_csv(fichier, sep='\t', index=False)
        print(f" Corpus sauvegardé dans {fichier}")

    @staticmethod
    def load(fichier="data/corpus.csv"):
        from DocumentFactory import DocumentFactory

        df = pd.read_csv(fichier, sep='\t')
        corpus = Corpus("Corpus chargé")

        for _, row in df.iterrows():
            if row['type'] == 'Reddit':
                doc = DocumentFactory.create_document(
                    source="Reddit",
                    titre=row['titre'],
                    auteur_or_auteurs=row['auteur'],
                    date=row['date'],
                    url=row['url'],
                    texte=row['texte'],
                    nb_commentaires=int(row['nb_commentaires']) if pd.notna(row['nb_commentaires']) else 0
                )
            elif row['type'] == 'Arxiv':
                auteurs = row['co_auteurs'].split(", ") if pd.notna(row['co_auteurs']) else [row['auteur']]
                doc = DocumentFactory.create_document(
                    source="Arxiv",
                    titre=row['titre'],
                    auteur_or_auteurs=auteurs,
                    date=row['date'],
                    url=row['url'],
                    texte=row['texte']
                )
            else:
                doc = DocumentFactory.create_document(
                    source="Document",
                    titre=row['titre'],
                    auteur_or_auteurs=row['auteur'],
                    date=row['date'],
                    url=row['url'],
                    texte=row['texte']
                )

            corpus.ajouter_document(doc)

        print(f"📂 Corpus chargé : {corpus.ndoc} documents, {corpus.naut} auteurs")
        return corpus

    # =====================================================================
    # REPRESENTATION
    # =====================================================================
    def __repr__(self):
        return f"Corpus '{self.nom}' : {self.ndoc} documents, {self.naut} auteurs"
