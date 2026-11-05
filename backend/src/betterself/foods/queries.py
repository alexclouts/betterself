
    # Fonction pour récupérer un aliment par son identifiant
from betterself.core.exceptions import RecordNotFound
from betterself.foods.models import Food
import uuid

"""
Retourne un aliment à partir de son identifiant ou lève une
exception s'il n'existe pas.
"""
def get_food_or_404(self, food_id: uuid.UUID) -> Food:
    food = self.db.get(Food, food_id)

    if food is None:
        raise RecordNotFound("Aucun aliment n'a été trouvé.")

    return food