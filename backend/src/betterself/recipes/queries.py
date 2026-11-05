import uuid

from sqlalchemy import select

from betterself.core.exceptions import RecordNotFound
from betterself.recipes.models import Recipe
from betterself.users.models import User



"""
Retourne une recette appartenant à l'utilisateur.
Lève `RecordNotFound` si la recette n'existe pas ou n'appartient pas à l'utilisateur.
"""
def get_recipe_or_404(
    self,
    user: User,
    recipe_id: uuid.UUID,
) -> Recipe:
    recipe = self.db.scalar(
        select(Recipe).where(
            Recipe.id == recipe_id,
            Recipe.user_id == user.id,
       )
        )
    # Aucun résultat trouvé, levée de l'exception RecordNotFound
    if recipe is None:
        raise RecordNotFound(
            "Aucune recette n'a été trouvée."
        )
    return recipe
