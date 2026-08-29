from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    name: str = Field(min_length=1, max_length=120)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: UUID
    email: EmailStr
    name: str | None
    onboarding_completed: bool
    email_notifications_enabled: bool

    model_config = {"from_attributes": True}


class UpdateUserPreferencesRequest(BaseModel):
    email_notifications_enabled: bool | None = None


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ForgotPasswordResponse(BaseModel):
    message: str
    # Only populated outside production, where no real email delivery
    # exists yet - see AuthService.request_password_reset.
    reset_token: str | None = None
    reset_url: str | None = None


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=8)


class DeleteAccountRequest(BaseModel):
    password: str
