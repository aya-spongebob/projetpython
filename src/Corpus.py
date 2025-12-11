from Document import Document, RedditDocument, ArxivDocument
from Author import Author
import pandas as pd
from datetime import datetime
import math
import re
from collections import defaultdict


class Corpus:
    def __init__(self, nom: str):
        self.nom = nom
        self.id2doc = {}
        self.authors = {}
        self.ndoc = 0
        self.naut = 0

        # Cache pour TD6
        self._big_string = None
        self.freq_table = None

        # Structures pour TD7
        self.index = None          # mot -> {doc_id: tf}
        self.idf = {}              # mot -> idf
        self.doc_norms = {}        # doc_id -> ||d|| (tf-idf)

    # =====================
    #   GESTION CORPUS
    # =====================

    def ajouter_document(self, doc: Document, doc_id: int = None):
        if doc_id is None:
            doc_id = self.ndoc

        self.id2doc[doc_id] = doc
        self.ndoc = len(self.id2doc)

        nom = doc.auteur
        if nom not in self.authors:
            self.authors[nom] = Author(nom)
        self.authors[nom].add(doc)
        self.naut = len(self.authors)

        # Invalider les caches
        self._big_string = None
        self.freq_table = None
        self.index = None
        self.idf = {}
        self.doc_norms = {}

    @classmethod
    def from_dataframe(cls, nom: str, df: pd.DataFrame):
        corpus = cls(nom)
        from DocumentFactory import DocumentFactory

        for _, row in df.iterrows():
            source = row.get("type", "Document")
            titre = row.get("titre", "")
            auteur = row.get("auteur", "")
            date = row.get("date", "")
            url = row.get("url", "")
            texte = row.get("texte", "") or ""
            nb_com = row.get("nb_commentaires", None)

            if pd.isna(texte):
                texte = ""
            if pd.isna(auteur):
                auteur = ""
            if pd.isna(nb_com):
                nb_com = None

            doc = DocumentFactory.create_document(
                source=source,
                titre=titre,
                auteur_or_auteurs=auteur,
                date=date,
                url=url,
                texte=str(texte),
                nb_commentaires=nb_com,
            )

            doc_id = int(row["id"]) if "id" in df.columns else None
            corpus.ajouter_document(doc, doc_id=doc_id)

        return corpus

    # =====================
    #   TD3 : STATISTIQUES
    # =====================

    def stats_documents(self):
        lignes = []
        for doc_id, doc in self.id2doc.items():
            texte = doc.texte or ""
            nb_car = len(texte)
            nb_mots = len(texte.split())
            nb_phrases = texte.count(".")
            lignes.append(
                {
                    "id": doc_id,
                    "nb_mots": nb_mots,
                    "nb_phrases": nb_phrases,
                    "nb_caracteres": nb_car,
                }
            )
        return pd.DataFrame(lignes)

    def chaine_concatenee(self):
        if self._big_string is None:
            self._big_string = " ".join(doc.texte for doc in self.id2doc.values())
        return self._big_string

    # =====================
    #   TD4 : TRI ET I/O
    # =====================

    def trier_par_titre(self, n=None):
        docs = sorted(self.id2doc.values(), key=lambda d: d.titre)
        if n is not None:
            docs = docs[:n]
        return docs

    def _date_to_timestamp(self, d):
        if isinstance(d, (int, float)):
            return float(d)
        if isinstance(d, str):
            d = d.strip()
            if not d:
                return 0.0
            # Timestamp Reddit (float)
            try:
                return float(d)
            except ValueError:
                pass
            # Date ISO Arxiv
            try:
                return datetime.fromisoformat(d.replace("Z", "+00:00")).timestamp()
            except Exception:
                return 0.0
        return 0.0

    def trier_par_date(self, n=None):
        docs = sorted(
            self.id2doc.values(),
            key=lambda d: self._date_to_timestamp(d.date),
            reverse=True,
        )
        if n is not None:
            docs = docs[:n]
        return docs

    def to_dataframe(self):
        lignes = []
        for doc_id, doc in self.id2doc.items():
            lignes.append(
                {
                    "id": doc_id,
                    "titre": doc.titre,
                    "auteur": doc.auteur,
                    "date": doc.date,
                    "url": doc.url,
                    "texte": doc.texte,
                    "type": getattr(
                        doc,
                        "source",
                        doc.getType() if hasattr(doc, "getType") else "Document",
                    ),
                    "nb_commentaires": getattr(doc, "nb_commentaires", None),
                }
            )
        return pd.DataFrame(lignes)

    def save(self, chemin: str):
        df = self.to_dataframe()
        df.to_csv(chemin, sep="\t", index=False)

    # =====================
    #   TD6 : SEARCH / CONCORDE / STATS
    # =====================

    def nettoyer_texte(self, texte: str) -> str:
        if not texte:
            return ""
        t = texte.lower()
        t = t.replace("\n", " ")
        t = re.sub(r"[^a-z0-9\s]", " ", t)
        t = re.sub(r"\s+", " ", t)
        return t.strip()

    def search_regex(self, pattern: str):
        chaine = self.chaine_concatenee()
        return [m.group() for m in re.finditer(pattern, chaine)]

    def concorde(self, pattern: str, contexte: int = 30):
        lignes = []
        for doc in self.id2doc.values():
            texte = doc.texte or ""
            for m in re.finditer(pattern, texte, flags=re.IGNORECASE):
                debut = max(0, m.start() - contexte)
                fin = min(len(texte), m.end() + contexte)
                lignes.append(
                    {
                        "contexte_gauche": texte[debut:m.start()],
                        "motif": texte[m.start():m.end()],
                        "contexte_droit": texte[m.end():fin],
                    }
                )
        return pd.DataFrame(lignes)

    def construire_vocabulaire(self):
        tf_global = defaultdict(int)
        df = defaultdict(int)

        for doc_id, doc in self.id2doc.items():
            texte_net = self.nettoyer_texte(doc.texte or "")
            mots = texte_net.split()
            vus = set()
            for mot in mots:
                tf_global[mot] += 1
                if mot not in vus:
                    df[mot] += 1
                    vus.add(mot)

        lignes = []
        for mot, tf in tf_global.items():
            lignes.append({"mot": mot, "TF": tf, "DF": df[mot]})

        table = pd.DataFrame(lignes)
        table = table.sort_values("TF", ascending=False).reset_index(drop=True)
        self.freq_table = table
        return table

    # =====================
    #   TD7 : INDEX + TF-IDF
    # =====================

    def construire_index(self):
        index = defaultdict(lambda: defaultdict(int))
        df = defaultdict(int)

        for doc_id, doc in self.id2doc.items():
            texte_net = self.nettoyer_texte(doc.texte or "")
            mots = texte_net.split()
            vus = set()
            for mot in mots:
                index[mot][doc_id] += 1
                if mot not in vus:
                    df[mot] += 1
                    vus.add(mot)

        n_docs = self.ndoc if self.ndoc else len(self.id2doc)
        idf = {}
        for mot, df_mot in df.items():
            idf[mot] = math.log((1 + n_docs) / (1 + df_mot)) + 1.0

        doc_norms = defaultdict(float)
        for mot, postings in index.items():
            w_idf = idf[mot]
            for doc_id, tf in postings.items():
                val = tf * w_idf
                doc_norms[doc_id] += val * val

        for d in doc_norms:
            doc_norms[d] = math.sqrt(doc_norms[d])

        self.index = index
        self.idf = idf
        self.doc_norms = doc_norms

    def search_advanced(self, requete: str, k: int = 5):
        if self.index is None:
            self.construire_index()

        texte_net = self.nettoyer_texte(requete)
        if not texte_net:
            return pd.DataFrame(columns=["score", "id", "titre", "auteur", "extrait"])

        q_tf = defaultdict(int)
        for mot in texte_net.split():
            if mot in self.idf:
                q_tf[mot] += 1

        if not q_tf:
            return pd.DataFrame(columns=["score", "id", "titre", "auteur", "extrait"])

        q_vec = {}
        for mot, tf in q_tf.items():
            q_vec[mot] = tf * self.idf[mot]

        q_norm = math.sqrt(sum(v * v for v in q_vec.values()))
        if q_norm == 0:
            return pd.DataFrame(columns=["score", "id", "titre", "auteur", "extrait"])

        scores = defaultdict(float)
        for mot, q_val in q_vec.items():
            postings = self.index.get(mot, {})
            idf_mot = self.idf[mot]
            for doc_id, tf in postings.items():
                d_val = tf * idf_mot
                scores[doc_id] += d_val * q_val

        resultats = []
        for doc_id, dot in scores.items():
            d_norm = self.doc_norms.get(doc_id, 0.0)
            if d_norm == 0:
                continue
            score = dot / (d_norm * q_norm)
            doc = self.id2doc[doc_id]
            extrait = (doc.texte or "")[:200].replace("\n", " ")
            resultats.append(
                {
                    "score": round(score, 4),
                    "id": doc_id,
                    "titre": doc.titre,
                    "auteur": doc.auteur,
                    "extrait": extrait + ("..." if len(extrait) == 200 else ""),
                }
            )

        resultats = sorted(resultats, key=lambda x: x["score"], reverse=True)
        if k is not None:
            resultats = resultats[:k]

        return pd.DataFrame(resultats)

    def __repr__(self):
        return f"Corpus '{self.nom}' : {self.ndoc} documents, {self.naut} auteurs"
