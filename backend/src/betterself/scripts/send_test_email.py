import sys

from betterself.core.config import settings
from betterself.core.email import get_email_sender

"""
Envoie un courriel de test avec la configuration SMTP actuelle (.env ou variables
d'environnement). Sert à vérifier les paramètres d'un fournisseur avant de déployer.

Utilisation, depuis le dossier backend :
    uv run python -m betterself.scripts.send_test_email destinataire@exemple.com

Contrairement à l'application, les erreurs ne sont pas masquées : le message du
serveur SMTP s'affiche (mauvais mot de passe, port bloqué, expéditeur refusé, etc.).
"""

if len(sys.argv) != 2:
    sys.exit("Utilisation : python -m betterself.scripts.send_test_email destinataire@exemple.com")

recipient = sys.argv[1]
print(
    f"Serveur : {settings.smtp_host}:{settings.smtp_port} "
    f"(STARTTLS : {settings.smtp_starttls}, SSL : {settings.smtp_ssl})"
)
print(f"Expéditeur : {settings.mail_from}")

get_email_sender().send(
    recipient,
    "Test d'envoi BetterSelf",
    "Si vous lisez ce message, la configuration SMTP de BetterSelf fonctionne.",
)
print(f"Courriel envoyé à {recipient}.")
