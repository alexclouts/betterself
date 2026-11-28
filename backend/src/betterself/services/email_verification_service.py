import logging
from datetime import datetime, timedelta, timezone

from betterself.core.config import settings
from betterself.core.email import EmailSender
from betterself.core.exceptions import IncorrectPassword, InvalidVerificationToken
from betterself.core.security import generate_email_token, hash_email_token, verify_password
from betterself.models.email_verification_models import EmailVerificationToken
from betterself.models.user_models import User
from betterself.repos.email_verification_repo import EmailVerificationRepository
from betterself.repos.user_repo import UserRepository

logger = logging.getLogger(__name__)

"""
Vérification de l'adresse courriel.

Le service crée les jetons et valide ceux reçus. Il ne fait pas l'envoi lui-même :
il retourne le courriel à envoyer. Le routeur enregistre d'abord les changements
dans la base de données, puis envoie le courriel en arrière-plan (BackgroundTasks).
Ainsi, un lien n'est jamais envoyé pour un jeton qui n'a pas été enregistré.

Chaque envoi est limité dans le temps, pour qu'on ne puisse pas inonder une
adresse de courriels en répétant une inscription ou une demande de renvoi.
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


    # Choisit le courriel à envoyer après une inscription. Retourne None si un
    # courriel semblable vient d'être envoyé à cette adresse.
    #   - Nouveau compte : lien de vérification.
    #   - Compte existant non vérifié : nouveau lien de vérification (la personne
    #     n'a peut-être jamais reçu le premier).
    #   - Compte existant vérifié : avis « vous avez déjà un compte ».
    def email_after_signup(self, user: User, created: bool) -> Email | None:
        if created:
            return self.issue(user)
        if user.email_verified_at is None:
            return self._resend_to(user)
        return self._account_exists_notice(user)


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
        # Le verrou empêche deux demandes simultanées de passer toutes les deux le délai minimal.
        user = self.user_repository.get_by_email_for_update(email)
        if user is None or user.email_verified_at is not None:
            return None
        return self._resend_to(user)


    # Valide le jeton reçu et le mot de passe du compte, puis marque l'adresse comme vérifiée.
    # Exiger le mot de passe garantit que la personne qui confirme l'adresse connaît
    # le mot de passe du compte : quelqu'un qui aurait inscrit l'adresse d'une autre
    # personne ne peut pas lui faire confirmer son compte à sa place. Un filtre
    # antipourriel qui ouvre le lien ne peut pas non plus confirmer l'adresse.
    # Lève InvalidVerificationToken si le jeton est inconnu, expiré ou déjà utilisé,
    # et IncorrectPassword si le mot de passe ne correspond pas (le jeton reste alors valide).
    def verify(self, token: str, password: str) -> User:
        now = datetime.now(timezone.utc)
        record = self.token_repository.get_by_hash(hash_email_token(token))

        if record is None or record.used_at is not None or record.expires_at <= now:
            raise InvalidVerificationToken()

        user = self.user_repository.get_by_id(record.user_id)
        if user is None:
            raise InvalidVerificationToken()

        if not verify_password(password, user.pwd_hash):
            raise IncorrectPassword()

        record.used_at = now
        if user.email_verified_at is None:
            user.email_verified_at = now
        return user


    # Nouveau lien, sauf si le dernier a été envoyé il y a moins du délai minimal.
    def _resend_to(self, user: User) -> Email | None:
        latest = self.token_repository.get_latest_for_user(user.id)
        min_delay = timedelta(seconds=settings.email_verification_resend_seconds)
        if latest is not None and datetime.now(timezone.utc) - latest.created_at < min_delay:
            return None
        return self.issue(user)


    # Avis « compte existant », au plus une fois par délai account_notice_cooldown_seconds.
    def _account_exists_notice(self, user: User) -> Email | None:
        now = datetime.now(timezone.utc)
        min_delay = timedelta(seconds=settings.account_notice_cooldown_seconds)
        if user.account_notice_sent_at is not None and now - user.account_notice_sent_at < min_delay:
            return None
        user.account_notice_sent_at = now
        return build_account_exists_email(user.email)


def build_verification_email(to: str, token: str) -> Email:
    link = f"{settings.frontend_url}/verify-email?token={token}"
    hours = settings.email_verification_expire_hours
    body = (
        "Bonjour,\n\n"
        "Merci de vous être inscrit à BetterSelf. Pour activer votre compte, "
        "ouvrez ce lien, puis entrez le mot de passe choisi à l'inscription :\n\n"
        f"{link}\n\n"
        f"Ce lien est valide pendant {hours} heures.\n\n"
        "Si vous n'avez pas créé de compte, ignorez simplement ce courriel.\n\n"
        "L'équipe BetterSelf"
    )
    return to, "Confirmez votre adresse courriel", body


# Envoyé quand quelqu'un tente de s'inscrire avec une adresse qui a déjà un compte vérifié.
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
