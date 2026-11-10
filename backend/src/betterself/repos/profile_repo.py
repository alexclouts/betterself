from sqlalchemy import select
from sqlalchemy.orm import Session

from betterself.core.exceptions import RecordNotFound
from betterself.models.user_models import User
from betterself.models.profile_models import UserProfile
from betterself.schemas.profile_schemas import UserProfileUpdate


"""
Gère le profil biométrique et les préférences d'un utilisateur.

Chaque utilisateur possède au plus un profil. Le premier appel à
`create_or_update_profile` crée le profil; les appels suivants le mettent à jour.
"""
class UserProfileRepository:
    def __init__(self, db: Session):
        self.db = db

    """
    Retourne le profil de l'utilisateur ou lève une exception si
    aucun profil n'a encore été créé.
    """
    def get_profile_or_404(self, user: User) -> UserProfile:
        profile = self.db.scalar(
            select(UserProfile).where(
                UserProfile.user_id == user.id,
            )
        )
        if profile is None:
            raise RecordNotFound(
                "Aucun profil utilisateur n'a été trouvé."
            )
        return profile


    """
    Crée le profil de l'utilisateur s'il n'existe pas, sinon met à jour le profil existant.
    Retourne un tuple contenant le profil et un booléen indiquant si le profil vient d'être créé.
    """
    def create_or_update_profile(
        self,
        user: User,
        data: UserProfileUpdate,
    ) -> tuple[UserProfile, bool]:

        profile = self.db.scalar(
            select(UserProfile).where(
                UserProfile.user_id == user.id,
            )
        )

        created = profile is None

        if profile is None:
            profile = UserProfile(
                user_id=user.id,
            )
            self.db.add(profile)

        profile.first_name = data.first_name
        profile.year_of_birth = data.year_of_birth
        profile.sex = data.sex
        profile.height_cm = data.height_cm
        profile.activity_level = data.activity_level

        self.db.flush()
        return profile, created