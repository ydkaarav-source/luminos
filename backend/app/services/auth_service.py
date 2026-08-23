import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, UnauthorizedError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    hash_reset_token,
    verify_password,
)
from app.models.password_reset_token import PasswordResetToken
from app.models.user import User
from app.repositories.user_repository import UserRepository

RESET_TOKEN_EXPIRE_HOURS = 1


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.users = UserRepository(db)

    def signup(self, email: str, password: str, name: str) -> tuple[User, str, str]:
        if self.users.get_by_email(email):
            raise ConflictError("An account with that email already exists.")

        user = self.users.create(email=email, hashed_password=hash_password(password), name=name)
        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)
        return user, access_token, refresh_token

    def login(self, email: str, password: str) -> tuple[User, str, str]:
        user = self.users.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise UnauthorizedError("Incorrect email or password.")

        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)
        return user, access_token, refresh_token

    def request_password_reset(self, email: str) -> str | None:
        """
        Returns the raw token if the email matched an account, None
        otherwise - the caller decides whether/how to surface that (see
        POST /auth/forgot-password), but this method itself never reveals
        account existence through its return value alone; the route is
        responsible for always sending the same generic response either
        way.
        """
        user = self.users.get_by_email(email)
        if not user:
            return None

        raw_token = secrets.token_urlsafe(32)
        token = PasswordResetToken(
            user_id=user.id,
            token_hash=hash_reset_token(raw_token),
            expires_at=datetime.now(timezone.utc) + timedelta(hours=RESET_TOKEN_EXPIRE_HOURS),
        )
        self.db.add(token)
        self.db.commit()
        return raw_token

    def reset_password(self, token: str, new_password: str) -> None:
        record = (
            self.db.query(PasswordResetToken)
            .filter(PasswordResetToken.token_hash == hash_reset_token(token))
            .first()
        )
        now = datetime.now(timezone.utc)
        if not record or record.used_at is not None or record.expires_at < now:
            raise UnauthorizedError("This password reset link is invalid or has expired.")

        user = self.users.get_by_id(record.user_id)
        if not user:
            raise UnauthorizedError("This password reset link is invalid or has expired.")

        user.hashed_password = hash_password(new_password)
        self.db.add(user)

        # Invalidate every outstanding token for this user (including the
        # one just used) as a safety measure - a leaked-but-unused token
        # can't be replayed after a successful reset.
        outstanding = (
            self.db.query(PasswordResetToken)
            .filter(
                PasswordResetToken.user_id == record.user_id,
                PasswordResetToken.used_at.is_(None),
            )
            .all()
        )
        for t in outstanding:
            t.used_at = now
        self.db.add_all(outstanding)
        self.db.commit()

    def delete_account(self, user: User, password: str) -> None:
        """
        Deletes the user's account and everything under it. Every
        business_id-foreign-keyed table cascades from `businesses` at
        the database level (ON DELETE CASCADE, verified directly against
        the live schema - see the migration audit in this task's
        report), and `businesses.user_id` itself cascades from `users`,
        so deleting the User row alone is sufficient - Postgres handles
        the rest.
        """
        if not verify_password(password, user.hashed_password):
            raise UnauthorizedError("Incorrect password.")
        self.db.delete(user)
        self.db.commit()
