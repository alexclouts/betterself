import smtplib
import ssl
from email.message import EmailMessage
from typing import Protocol

from betterself.core.config import settings

"""
Envoi des courriels.

Le code de l'application dépend seulement de l'interface EmailSender, jamais
directement de SMTP. On peut ainsi remplacer l'envoi réel par un faux pendant
les tests (voir FakeEmailSender dans tests/conftest.py) ou changer de fournisseur
sans toucher aux services.
"""


class EmailSender(Protocol):
    def send(self, to: str, subject: str, body: str) -> None: ...


# Envoie les courriels par SMTP. En développement, le serveur est Mailpit.
class SmtpEmailSender:
    def __init__(
        self,
        host: str,
        port: int,
        mail_from: str,
        user: str | None = None,
        password: str | None = None,
        starttls: bool = False,
        use_ssl: bool = False,
        reply_to: str | None = None,
    ):
        # Un identifiant SMTP ne doit jamais circuler en clair sur le réseau.
        if user and password and not (starttls or use_ssl):
            raise ValueError(
                "SMTP_USER et SMTP_PASSWORD exigent un chiffrement : "
                "SMTP_STARTTLS=true (port 587) ou SMTP_SSL=true (port 465)."
            )
        if starttls and use_ssl:
            raise ValueError("Choisir SMTP_STARTTLS ou SMTP_SSL, pas les deux.")

        self.host = host
        self.port = port
        self.mail_from = mail_from
        self.user = user
        self.password = password
        self.starttls = starttls
        self.use_ssl = use_ssl
        self.reply_to = reply_to


    def send(self, to: str, subject: str, body: str) -> None:
        message = EmailMessage()
        message["From"] = self.mail_from
        message["To"] = to
        message["Subject"] = subject
        # Les réponses des utilisateurs arrivent à cette adresse plutôt qu'à l'expéditeur.
        if self.reply_to:
            message["Reply-To"] = self.reply_to
        message.set_content(body)

        # Sans contexte explicite, smtplib chiffre sans vérifier le certificat du
        # serveur : le mot de passe SMTP pourrait alors être intercepté.
        context = ssl.create_default_context()

        # Le délai évite qu'un serveur SMTP qui ne répond pas bloque indéfiniment.
        if self.use_ssl:
            connection = smtplib.SMTP_SSL(self.host, self.port, timeout=10, context=context)
        else:
            connection = smtplib.SMTP(self.host, self.port, timeout=10)

        with connection as smtp:
            if self.starttls:
                smtp.starttls(context=context)
            if self.user and self.password:
                smtp.login(self.user, self.password)
            smtp.send_message(message)


# Dépendance FastAPI. Les tests la remplacent avec app.dependency_overrides.
def get_email_sender() -> EmailSender:
    return SmtpEmailSender(
        host=settings.smtp_host,
        port=settings.smtp_port,
        mail_from=settings.mail_from,
        user=settings.smtp_user,
        password=settings.smtp_password,
        starttls=settings.smtp_starttls,
        use_ssl=settings.smtp_ssl,
        reply_to=settings.mail_reply_to,
    )
