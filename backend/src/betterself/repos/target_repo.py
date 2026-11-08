from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from betterself.models.target_models import GoalTarget
from betterself.models.user_models import User


class TargetRepository:
    def __init__(self, db: Session):
        self.db = db

    # Récupère le target actif pour un utilisateur donné.
    # Un target est considéré actif si sa date de validité de fin est nulle.
    def get_active_for_user(
        self,
        user: User,
    ) -> GoalTarget | None:
        query = (
            select(GoalTarget)
            .where(
                GoalTarget.user_id == user.id,
                GoalTarget.valid_until.is_(None),
            )
            .order_by(GoalTarget.valid_from.desc())
            .limit(1)
        )
        return self.db.scalar(query)


    # Ajoute un nouveau target pour un utilisateur donné.
    def add(
        self,
        target: GoalTarget,
    ) -> GoalTarget:
        self.db.add(target)
        self.db.commit()
        self.db.refresh(target)
        return target


    # Ferme un target existant en définissant sa date de validité de fin.
    def close(
        self,
        target: GoalTarget,
        closed_at: date,
    ) -> GoalTarget:
        target.valid_until = closed_at
        self.db.commit()
        return target