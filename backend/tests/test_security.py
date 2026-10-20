from betterself.core.security import verify_password, hash_password

def test_hash_password():
    password = "mysecretpassword"
    hashed = hash_password(password)
    assert hashed != password  # Le mot de passe haché ne doit pas être identique au mot de passe original

def test_verify_password():
    password = "mysecretpassword"
    hashed = hash_password(password)

    assert verify_password(password, hashed)  # Le mot de passe original devrait correspondre au mot de passe haché
    assert not verify_password("wrongpassword", hashed)  # Un mot de passe incorrect ne devrait pas correspondre au mot de passe haché
