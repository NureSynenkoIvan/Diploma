import base64
import hashlib
import secrets

_PBKDF2_ALGO = "sha256"
_PBKDF2_ITERATIONS = 120_000
_PBKDF2_SALT_BYTES = 16

def hash_password(password: str) -> str:
    salt = secrets.token_bytes(_PBKDF2_SALT_BYTES)
    digest = hashlib.pbkdf2_hmac(_PBKDF2_ALGO, password.encode("utf-8"), salt, _PBKDF2_ITERATIONS)
    salt_b64 = base64.b64encode(salt).decode("ascii")
    digest_b64 = base64.b64encode(digest).decode("ascii")
    return f"pbkdf2_{_PBKDF2_ALGO}${_PBKDF2_ITERATIONS}${salt_b64}${digest_b64}"