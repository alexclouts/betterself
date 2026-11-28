class RecordNotFound(Exception):
    def __init__(self, message="Entrée introuvable dans la base de données"):
        self.message = message
        super().__init__(self.message)

class DuplicateRecord(Exception):
    def __init__(self, message="Entrée déjà existante dans la base de données"):
        self.message = message
        super().__init__(self.message)

# L'opération laisserait une recette sans ingrédient.
class RecipeWithoutIngredients(Exception):
    def __init__(self, message="Une recette doit contenir au moins un ingrédient."):
        self.message = message
        super().__init__(self.message)

# Le catalogue Open Food Facts est absent ou illisible.
class CatalogUnavailable(Exception):
    def __init__(self, message="Le catalogue Open Food Facts est indisponible"):
        self.message = message
        super().__init__(self.message)

# Le lien de vérification du courriel est inconnu, expiré ou déjà utilisé.
class InvalidVerificationToken(Exception):
    def __init__(self, message="Ce lien de vérification est invalide ou expiré."):
        self.message = message
        super().__init__(self.message)
