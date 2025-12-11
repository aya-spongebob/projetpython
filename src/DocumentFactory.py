
from Document import Document, RedditDocument, ArxivDocument

class DocumentFactory:
    @staticmethod
    def create_document(source, titre, auteur_or_auteurs, date, url, texte, nb_commentaires=None):
        if source == "Reddit":
            return RedditDocument(titre, auteur_or_auteurs, date, url, texte, nb_commentaires)
        elif source == "Arxiv":
            return ArxivDocument(titre, auteur_or_auteurs, date, url, texte)
        else:
            return Document(titre, auteur_or_auteurs, date, url, texte)
