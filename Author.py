# Author.py

class Author:
    def __init__(self, name):
        self.name = name
        self.ndoc = 0
        self.production = {}   # dictionnaire doc_id → Document

    def add(self, doc):
        self.production[self.ndoc] = doc
        self.ndoc += 1

    def __str__(self):
        return f"Auteur : {self.name}, {self.ndoc} documents"
