class Document:
    def __init__(self, titre, auteur, date, url, texte, source="Document"):
        self.titre = titre
        self.auteur = auteur
        
        self.date = date
        self.url = url
        self.texte = texte
        
        self.source = source

    def afficher_infos(self):
        """Affiche toutes les informations du document"""
        
        print(f"Titre : {self.titre}")
        print(f"Auteur : {self.auteur}")
        print(f"Date : {self.date}")
        print(f"URL : {self.url}")
        print(f"Texte : {self.texte[:200]}...")
        print(f"Type : {self.getType()}")

    def getType(self):
        """Retourne le type de document"""
        return self.source

    def __str__(self):
        return f"Document : {self.titre} ({self.auteur})"


class RedditDocument(Document):
    def __init__(self, titre, auteur, date, url, texte, nb_commentaires):
        super().__init__(titre, auteur, date, url, texte, source="Reddit")
        self.nb_commentaires = nb_commentaires

    def getNbCommentaires(self):
        """Retourne le nombre de commentaires"""
        return self.nb_commentaires
    
    def setNbCommentaires(self, nb):
        """Définit le nombre de commentaires"""
        self.nb_commentaires = nb

    def getType(self):
        """Retourne le type de document"""
        return "Reddit"

    def __str__(self):
        return f"[Reddit] {self.titre} ({self.auteur}) - 💬 {self.nb_commentaires} commentaires"


class ArxivDocument(Document):
    def __init__(self, titre, auteurs, date, url, texte):
       
        super().__init__(titre, ", ".join(auteurs), date, url, texte, source="Arxiv")
        self.auteurs = auteurs  # Liste des co-auteurs

    def getCoAuteurs(self):
        
        """Retourne la liste des co-auteurs"""
        return self.auteurs
    
    def setCoAuteurs(self, auteurs):
        
        """Définit la liste des co-auteurs"""
        self.auteurs = auteurs
        self.auteur = ", ".join(auteurs)

    def getType(self):
        """Retourne le type de document"""
        
        
        return "Arxiv"

    def __str__(self):
        
        return f"[Arxiv] {self.titre} ({', '.join(self.auteurs)}, {self.date})"