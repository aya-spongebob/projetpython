# DocumentFactory.py

from Document import Document, RedditDocument, ArxivDocument

class DocumentFactory:
    @staticmethod
    def create_document(source, titre, auteur_or_auteurs, date, url, texte, nb_commentaires=None):

        if source == "Reddit":
            return RedditDocument(
                titre=titre,
                auteur=auteur_or_auteurs,
                date=date,
                url=url,
                texte=texte,
                nb_commentaires=nb_commentaires
            )

        elif source == "Arxiv":
            return ArxivDocument(
                titre=titre,
                auteurs=auteur_or_auteurs,
                date=date,
                url=url,
                texte=texte
            )

        else:
            return Document(
                titre=titre,
                auteur=auteur_or_auteurs,
                date=date,
                url=url,
                texte=texte
            )
