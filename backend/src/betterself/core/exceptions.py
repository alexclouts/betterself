class RecordNotFound(Exception):
    def __init__(self, message="Entrée introuvable dans la base de données"):
        self.message = message
        super().__init__(self.message)