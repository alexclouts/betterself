import logging
from datetime import datetime, timedelta, timezone

from betterself.core.config import settings
from betterself.core.email import EmailSender
from betterself.core.exceptions import InvalidVerificationToken
from betterself.core.security import generate_email_token, hash_email_token
from betterself.models.email_verification_models import EmailVerificationToken
from betterself.models.user_models import User
from betterself.repos.email_verification_repo import EmailVerificationRepository
from betterself.repos.user_repo import UserRepository

logger = logging.getLogger(__name__)

"""
Vérification de l'adresse courriel.

Le service crée les jetons et valide ceux reçus. Il ne fait pas l'envoi lui-même :
il retourne le courriel à envoyer, et le routeur l'envoie en arrière-plan
(BackgroundTasks) pour que la requête n'attende pas le serveur SMTP.
"""

# Courriel prêt à être envoyé.
Email = tuple[str, str, str]  # (destinataire, sujet, contenu)


class EmailVerificationService:
    def __init__(
        self,
        token_repository: EmailVerificationRepository,
        user_repository: UserRepository,
    ):
        self.token_repository = token_repository
        self.user_repository = user_repository


    # Crée un nouveau jeton pour l'utilisateur et retourne le courriel contenant le lien.
    # Les liens envoyés précédemment cessent de fonctionner.
    def issue(self, user: User) -> Email:
        now = datetime.now(timezone.utc)
        token, token_hash = generate_email_token()

        self.token_repository.invalidate_for_user(user.id, now)
        self.token_repository.add(
            EmailVerificationToken(
                user_id=user.id,
                token_hash=token_hash,
                created_at=now,
                expires_at=now + timedelta(hours=settings.email_verification_expire_hours),
            )
        )
        return build_verification_email(user.email, token)


    # Renvoie un lien de vérification si c'est pertinent. Retourne None sinon :
    # adresse inconnue, déjà vérifiée, ou lien envoyé il y a trop peu de temps.
    # Le routeur répond la même chose dans tous les cas, pour ne pas révéler
    # quelles adresses ont un compte.
    def resend(self, email: str) -> Email | None:
        user = self.user_repository.get_by_email(email)
        if user is None or user.email_verified_at is not None:
            return None

        latest = self.token_repository.get_latest_for_user(user.id)
        min_delay = timedelta(seconds=settings.email_verification_resend_seconds)
        if latest is not None and datetime.now(timezone.utc) - latest.created_at < min_delay:
            return None

        return self.issue(user)


    # Valide le jeton reçu et marque l'adresse de son utilisateur comme vérifiée.
    # Lève InvalidVerificationToken si le jeton est inconnu, expiré ou déjà utilisé.
    def verify(self, token: str) -> User:
        now = datetime.now(timezone.utc)
        record = self.token_repository.get_by_hash(hash_email_token(token))

        if record is None or record.used_at is not None or record.expires_at <= now:
            raise InvalidVerificationToken()

        user = self.user_repository.get_by_id(record.user_id)
        if user is None:
            raise InvalidVerificationToken()

        record.used_at = now
        if user.email_verified_at is None:
            user.email_verified_at = now
        return user


def build_verification_email(to: str, token: str) -> Email:
    link = f"{settings.frontend_url}/verify-email?token={token}"
    hours = settings.email_verification_expire_hours
    body = (
        "Bonjour,\n\n"
        "Merci de vous être inscrit à BetterSelf. Pour activer votre compte, "
        "confirmez votre adresse courriel en ouvrant ce lien :\n\n"
        f"{link}\n\n"
        f"Ce lien est valide pendant {hours} heures.\n\n"
        "Si vous n'avez pas créé de compte, ignorez simplement ce courriel.\n\n"
        "L'équipe BetterSelf"
    )
    return to, "Confirmez votre adresse courriel", body


# Envoyé quand quelqu'un tente de s'inscrire avec une adresse qui a déjà un compte.
# La réponse de l'API est identique à une inscription réussie : seul le propriétaire
# de l'adresse apprend que le compte existe.
def build_account_exists_email(to: str) -> Email:
    body = (
        "Bonjour,\n\n"
        "Quelqu'un, peut-être vous, a tenté de créer un compte BetterSelf avec "
        "cette adresse courriel. Un compte existe déjà avec cette adresse : "
        "vous pouvez simplement vous connecter.\n\n"
        f"{settings.frontend_url}/login\n\n"
        "Si ce n'est pas vous, ignorez ce courriel : votre compte n'a pas été modifié.\n\n"
        "L'équipe BetterSelf"
    )
    return to, "Vous avez déjà un compte BetterSelf", body


# Tâche d'arrière-plan : un échec d'envoi est journalisé sans faire échouer la requête.
# L'utilisateur peut toujours redemander le lien.
def send_email(sender: EmailSender, email: Email) -> None:
    to, subject, body = email
    try:
        sender.send(to, subject, body)
    except Exception:
        logger.exception("Échec de l'envoi du courriel « %s »", subject)
