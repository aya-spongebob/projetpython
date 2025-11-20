# CorpusSingleton.py

from Corpus import Corpus

class CorpusSingleton(Corpus):
    _instance = None

    def __new__(cls, nom):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.__init__(nom)  # première initialisation
        return cls._instance
