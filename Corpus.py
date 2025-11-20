
from Document import Document, RedditDocument, ArxivDocument
from Author import Author
import pandas as pd
from datetime import datetime



class Corpus:
    def __init__(self, nom):
        self.nom = nom
        self.id2doc = {}
        self.authors = {}
        self.ndoc = 0
        
        self.naut = 0

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

    # =====MÉTHODES D'AFFICHAGE TRIÉES =====
    
    def afficher_par_titre(self, n=None):
        """Affiche les documents triés par titre (ordre alphabétique)"""
        
        docs_tries = sorted(self.id2doc.values(), key=lambda d: d.titre.lower())
        if n is not None:
            docs_tries = docs_tries[:n]
        for doc in docs_tries:
            print(doc)

    def afficher_par_date(self, n=None):
        """Affiche les documents triés par date """
        
        def get_date_sortable(doc):
            """Convertit la date """
            if isinstance(doc.date, (int, float)):
                # (Reddit)
                return doc.date
            elif isinstance(doc.date, str):
                #  convertir en timestamp
                try:
                    dt = datetime.fromisoformat(doc.date.replace('Z', '+00:00'))
                    
                    return dt.timestamp()
                except:
                    return 0
            return 0
        
        docs_tries = sorted(self.id2doc.values(), key=get_date_sortable, reverse=True)
        if n is not None:
            docs_tries = docs_tries[:n]
        for doc in docs_tries:
            print(doc)

    # ===== STATISTIQUES AUTEUR =====
    
    def statistiques_auteur(self, nom_auteur):
        """Affiche les statistiques pour un auteur donné"""
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
        

    # =====MANIPULATIONS DES DONNÉES =====
    
    def afficher_stats_basiques(self):
        """TD3.3.1 et 3.2 : Affiche la taille du corpus et stats par document"""
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
    
    def supprimer_documents_courts(self, min_length=20):
       
        docs_a_supprimer = []
        
        for doc_id, doc in self.id2doc.items():
            if len(doc.texte) < min_length:
                docs_a_supprimer.append(doc_id)
        
        for doc_id in docs_a_supprimer:
            del self.id2doc[doc_id]
        
        self.ndoc = len(self.id2doc)
        
        print(f"\n  {len(docs_a_supprimer)} documents de moins de {min_length} caractères supprimés.")
        print(f"Nouveau nombre de documents : {self.ndoc}")
    
    def concatener_textes(self):
        """ Crée une chaîne unique avec tous les documents"""
        textes = [doc.texte for doc in self.id2doc.values()]
        texte_complet = " ".join(textes)
        
        print(f"\n📝 Chaîne unique créée :")
        print(f"   - Longueur totale : {len(texte_complet)} caractères")
        print(f"   - Nombre de mots : {len(texte_complet.split())}")
        print(f"   - Extrait : {texte_complet[:150]}...")
        
        return texte_complet

    # ===== TD4 Partie 3.3 et 3.4 : SAUVEGARDE ET CHARGEMENT =====
    
    def save(self, fichier="data/corpus.csv"):
        """Sauvegarde le corpus dans un fichier CSV"""
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
        """Charge un corpus depuis un fichier CSV"""
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

    #  __repr__ =====
    
    def __repr__(self):
        return f"Corpus '{self.nom}' : {self.ndoc} documents, {self.naut} auteurs"