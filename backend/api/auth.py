from __future__ import annotations

import base64
import hashlib
import hmac
import secrets
from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from db.models import User
from db.session import get_db

router = APIRouter(prefix="/auth", tags=["Auth"])

_TOKEN_TO_USER_ID: Dict[str, int] = {}
_bearer = HTTPBearer(auto_error=False)

_PBKDF2_ALGO = "sha256"
_PBKDF2_ITERATIONS = 120_000
_PBKDF2_SALT_BYTES = 16


class LoginRequest(BaseModel):
    login: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(_PBKDF2_SALT_BYTES)
    digest = hashlib.pbkdf2_hmac(_PBKDF2_ALGO, password.encode("utf-8"), salt, _PBKDF2_ITERATIONS)
    salt_b64 = base64.b64encode(salt).decode("ascii")
    digest_b64 = base64.b64encode(digest).decode("ascii")
    return f"pbkdf2_{_PBKDF2_ALGO}${_PBKDF2_ITERATIONS}${salt_b64}${digest_b64}"


def verify_password(password: str, stored_hash: str) -> bool:
    # Backward compatibility with existing seed data where password_hash stores raw password.
    if "$" not in stored_hash:
        return hmac.compare_digest(stored_hash, password)

    try:
        method, iterations_raw, salt_b64, digest_b64 = stored_hash.split("$", 3)
        if method != f"pbkdf2_{_PBKDF2_ALGO}":
            return False

        iterations = int(iterations_raw)
        salt = base64.b64decode(salt_b64.encode("ascii"))
        expected_digest = base64.b64decode(digest_b64.encode("ascii"))
    except (ValueError, TypeError):
        return False

    actual_digest = hashlib.pbkdf2_hmac(
        _PBKDF2_ALGO, password.encode("utf-8"), salt, iterations
    )
    return hmac.compare_digest(expected_digest, actual_digest)


def require_auth(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    user_id = _TOKEN_TO_USER_ID.get(credentials.credentials)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    user = db.get(User, user_id)
    if user is None:
        _TOKEN_TO_USER_ID.pop(credentials.credentials, None)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    return user


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> LoginResponse:
    user = db.execute(select(User).where(User.login == payload.login)).scalar_one_or_none()
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid login or password",
        )

    token = secrets.token_urlsafe(32)
    _TOKEN_TO_USER_ID[token] = user.id
    return LoginResponse(access_token=token)
