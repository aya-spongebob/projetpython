from Corpus import Corpus

class CorpusSingleton(Corpus):
    _instance = None

    def __new__(cls, nom):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            super(CorpusSingleton, cls._instance).__init__(nom)  # Initialisation une seule fois
        return cls._instance
