from sqlalchemy import select
from sqlalchemy.orm import Session

from betterself.core.exceptions import RecordNotFound
from betterself.users.models import User
from betterself.profile.models import UserProfile
from betterself.profile.schemas import UserProfileUpdate


class UserProfileService:
    """
    Gère le profil biométrique et les préférences d'un utilisateur.

    Chaque utilisateur possède au plus un profil. Le premier appel à
    `create_or_update_profile` crée le profil; les appels suivants le
    mettent à jour.
    """

    def __init__(self, db: Session):
        self.db = db

    # Fonction pour récupérer le profil d'un utilisateur
    def get_profile_or_404(self, user: User) -> UserProfile:
        """
        Retourne le profil de l'utilisateur ou lève une exception si
        aucun profil n'a encore été créé.
        """
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

    # Fonction pour créer le profil s'il n'existe pas, sinon le mettre à jour
    def create_or_update_profile(
        self,
        user: User,
        data: UserProfileUpdate,
    ) -> tuple[UserProfile, bool]:
        """
        Crée le profil de l'utilisateur s'il n'existe pas, sinon met à jour
        le profil existant.

        Retourne un tuple contenant le profil et un booléen indiquant si
        le profil vient d'être créé.
        """
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

        self.db.commit()
        self.db.refresh(profile)

        return profile, created