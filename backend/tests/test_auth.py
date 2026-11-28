from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient
from sqlalchemy import select

from betterself.core.config import settings
from betterself.core.security import hash_email_token
from betterself.models.email_verification_models import EmailVerificationToken
from betterself.models.user_models import User
from betterself.routers.auth_router import CHECK_INBOX_MESSAGE
from tests.utils import last_verification_token, registered_user
from tests.api_helpers import AUTH_URL
"""
Tests pour l'enregistrement d'un utilisateur. Ces tests vérifient que le processus d'enregistrement fonctionne correctement pour différents scénarios,
tels que l'enregistrement réussi et l'enregistrement avec un email déjà existant.
Les tests utilisent un client de test FastAPI pour effectuer des requêtes HTTP vers l'application.
"""

# Test de l'enregistrement d'un nouvel utilisateur : compte non vérifié et lien envoyé
def test_register_user_success(client: TestClient, email_sender, test_session):
    response = client.post(
        f"{AUTH_URL}/register",
        json={"email": "Test@Example.com", "password": "testpassword"}
    )
    assert response.status_code == 202
    assert response.json() == {"message": CHECK_INBOX_MESSAGE}

    user = test_session.scalar(select(User).where(User.email == "test@example.com"))
    assert user is not None
    assert user.email_verified_at is None

    # Un seul courriel, envoyé à l'adresse en minuscules, avec le lien vers le frontend
    assert len(email_sender.sent) == 1
    assert email_sender.sent[0]["to"] == "test@example.com"
    assert f"{settings.frontend_url}/verify-email?token=" in email_sender.sent[0]["body"]

    # Seul le hash du jeton est stocké, jamais le jeton en clair
    token = last_verification_token(client, "test@example.com")
    stored = test_session.scalar(select(EmailVerificationToken))
    assert stored.token_hash == hash_email_token(token)
    assert stored.token_hash != token


# Une adresse déjà inscrite reçoit la même réponse : l'API ne révèle pas qu'elle existe.
# Le propriétaire de l'adresse est prévenu par courriel, et son mot de passe ne change pas.
def test_register_user_existing_email(client: TestClient, email_sender, registered_user):
    response = client.post(
        f"{AUTH_URL}/register",
        json={"email": "test@example.com", "password": "otherpassword"},
    )

    assert response.status_code == 202
    assert response.json() == {"message": CHECK_INBOX_MESSAGE}
    assert email_sender.sent[-1]["subject"] == "Vous avez déjà un compte BetterSelf"
    assert "verify-email" not in email_sender.sent[-1]["body"]

    login = client.post(f"{AUTH_URL}/login", data={"username": "test@example.com", "password": "otherpassword"})
    assert login.status_code == 401


# Un échec d'envoi du courriel ne fait pas échouer l'inscription
def test_register_survives_email_failure(client: TestClient, email_sender, monkeypatch):
    def fail(to, subject, body):
        raise ConnectionRefusedError("SMTP indisponible")

    monkeypatch.setattr(email_sender, "send", fail)
    response = client.post(f"{AUTH_URL}/register", json={"email": "test@example.com", "password": "testpassword"})

    assert response.status_code == 202


"""
Tests pour la connexion d'un utilisateur. Ces tests vérifient que l'authentification fonctionne correctement pour différents scénarios, 
tels que la connexion réussie, la connexion avec un mot de passe incorrect et la connexion avec un email inconnu. 
Les tests utilisent un utilisateur enregistré pour valider le processus de connexion.
"""

# Test de la connexion d'un utilisateur avec des informations correctes
def test_login_success(client: TestClient, registered_user):
    response = client.post(
        f"{AUTH_URL}/login",
        data={"username": "test@example.com", "password": "testpassword"}
    )

    # Vérification que la réponse contient un token d'accès et le type de token attendu
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


# Test de la connexion d'un utilisateur avec un mot de passe incorrect
def test_login_wrong_password(client: TestClient, registered_user):
    response = client.post(
        f"{AUTH_URL}/login",
        data={"username": "test@example.com", "password": "wrongpassword"}
    )

    # Vérification que la réponse contient un message d'erreur
    assert response.status_code == 401
    assert response.json() == {"detail": "Les informations entrées sont invalides."}


# Test de la connexion d'un utilisateur avec un email inconnu
def test_login_unknown_email(client: TestClient):
    response = client.post(
        "/auth/login",
        data={"username": "unknown@example.com", "password": "testpassword"}
    )

    # Vérification que la réponse contient un message d'erreur
    assert response.status_code == 401
    assert response.json() == {"detail": "Les informations entrées sont invalides."}


# Une erreur de base de données ne doit pas exposer la requête SQL au client.
def test_register_hides_database_error(client: TestClient, monkeypatch):
    from sqlalchemy.exc import OperationalError
    from betterself.services.user_service import UserService

    def fail(self, data):
        raise OperationalError("INSERT INTO users (email) VALUES (%(email)s)", {}, Exception("secret"))

    monkeypatch.setattr(UserService, "create_user", fail)
    response = client.post(
        f"{AUTH_URL}/register",
        json={"email": "test@example.com", "password": "testpassword"},
        headers={"Origin": "http://localhost:8080"},
    )

    assert response.status_code == 500
    assert response.json() == {"detail": "Une erreur interne est survenue. Réessayez plus tard."}
    assert "INSERT" not in response.text and "secret" not in response.text
    # La réponse passe par CORSMiddleware : le navigateur peut la lire.
    assert response.headers["access-control-allow-origin"] == "http://localhost:8080"



# Le mot de passe est correct mais l'adresse n'est pas confirmée : connexion refusée
def test_login_unverified_email(client: TestClient):
    client.post(f"{AUTH_URL}/register", json={"email": "test@example.com", "password": "testpassword"})

    response = client.post(f"{AUTH_URL}/login", data={"username": "test@example.com", "password": "testpassword"})

    assert response.status_code == 403
    assert response.json() == {"detail": "Veuillez confirmer votre adresse courriel avant de vous connecter."}


# Un mauvais mot de passe sur un compte non vérifié donne la même erreur qu'ailleurs :
# on n'apprend pas que le compte existe sans connaître son mot de passe.
def test_login_unverified_wrong_password(client: TestClient):
    client.post(f"{AUTH_URL}/register", json={"email": "test@example.com", "password": "testpassword"})

    response = client.post(f"{AUTH_URL}/login", data={"username": "test@example.com", "password": "wrongpassword"})

    assert response.status_code == 401


"""
Tests pour la confirmation de l'adresse courriel avec le lien reçu.
"""

def register(client: TestClient, email: str = "test@example.com") -> str:
    client.post(f"{AUTH_URL}/register", json={"email": email, "password": "testpassword"})
    return last_verification_token(client, email)


def login_status(client: TestClient, email: str = "test@example.com") -> int:
    return client.post(f"{AUTH_URL}/login", data={"username": email, "password": "testpassword"}).status_code


# Le lien reçu confirme l'adresse, puis la connexion fonctionne
def test_verify_email_success(client: TestClient, test_session):
    token = register(client)

    response = client.post(f"{AUTH_URL}/verify-email", json={"token": token})

    assert response.status_code == 200
    user = test_session.scalar(select(User).where(User.email == "test@example.com"))
    assert user.email_verified_at is not None
    assert login_status(client) == 200


# Un jeton ne sert qu'une fois
def test_verify_email_token_single_use(client: TestClient):
    token = register(client)
    client.post(f"{AUTH_URL}/verify-email", json={"token": token})

    response = client.post(f"{AUTH_URL}/verify-email", json={"token": token})

    assert response.status_code == 400
    assert response.json() == {"detail": "Ce lien de vérification est invalide ou expiré."}


# Un jeton inventé est refusé
def test_verify_email_unknown_token(client: TestClient):
    response = client.post(f"{AUTH_URL}/verify-email", json={"token": "jeton-invente"})

    assert response.status_code == 400
    assert login_status(client) == 401


# Un jeton expiré est refusé et l'adresse reste non vérifiée
def test_verify_email_expired_token(client: TestClient, test_session):
    token = register(client)
    stored = test_session.scalar(select(EmailVerificationToken))
    stored.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
    test_session.flush()

    response = client.post(f"{AUTH_URL}/verify-email", json={"token": token})

    assert response.status_code == 400
    assert login_status(client) == 403


# Un jeton vide ou démesuré est rejeté par la validation
def test_verify_email_invalid_payload(client: TestClient):
    assert client.post(f"{AUTH_URL}/verify-email", json={"token": ""}).status_code == 422
    assert client.post(f"{AUTH_URL}/verify-email", json={"token": "a" * 129}).status_code == 422


"""
Tests pour le renvoi du lien de vérification.
"""

# Fait comme si le dernier lien avait été envoyé avant le délai minimal entre deux envois
def age_latest_token(test_session):
    stored = test_session.scalars(
        select(EmailVerificationToken).order_by(EmailVerificationToken.created_at.desc())
    ).first()
    stored.created_at -= timedelta(seconds=settings.email_verification_resend_seconds + 1)
    test_session.flush()


# Un nouveau lien est envoyé et l'ancien cesse de fonctionner
def test_resend_verification_replaces_token(client: TestClient, email_sender, test_session):
    old_token = register(client)
    age_latest_token(test_session)

    response = client.post(f"{AUTH_URL}/resend-verification", json={"email": "test@example.com"})

    assert response.status_code == 202
    assert response.json() == {"message": CHECK_INBOX_MESSAGE}
    assert len(email_sender.sent) == 2
    new_token = last_verification_token(client, "test@example.com")
    assert new_token != old_token

    assert client.post(f"{AUTH_URL}/verify-email", json={"token": old_token}).status_code == 400
    assert client.post(f"{AUTH_URL}/verify-email", json={"token": new_token}).status_code == 200


# Deux demandes rapprochées n'envoient qu'un seul courriel
def test_resend_verification_rate_limited(client: TestClient, email_sender):
    register(client)

    response = client.post(f"{AUTH_URL}/resend-verification", json={"email": "test@example.com"})

    assert response.status_code == 202
    assert len(email_sender.sent) == 1


# Adresse inconnue ou déjà vérifiée : même réponse, aucun courriel
def test_resend_verification_unknown_or_verified(client: TestClient, email_sender, registered_user):
    sent_before = len(email_sender.sent)

    unknown = client.post(f"{AUTH_URL}/resend-verification", json={"email": "unknown@example.com"})
    verified = client.post(f"{AUTH_URL}/resend-verification", json={"email": "test@example.com"})

    assert unknown.status_code == verified.status_code == 202
    assert unknown.json() == verified.json() == {"message": CHECK_INBOX_MESSAGE}
    assert len(email_sender.sent) == sent_before
