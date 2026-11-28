import smtplib
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
    ):
        self.host = host
        self.port = port
        self.mail_from = mail_from
        self.user = user
        self.password = password
        self.starttls = starttls


    def send(self, to: str, subject: str, body: str) -> None:
        message = EmailMessage()
        message["From"] = self.mail_from
        message["To"] = to
        message["Subject"] = subject
        message.set_content(body)

        # Le délai évite qu'un serveur SMTP qui ne répond pas bloque indéfiniment.
        with smtplib.SMTP(self.host, self.port, timeout=10) as smtp:
            if self.starttls:
                smtp.starttls()
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
    )
