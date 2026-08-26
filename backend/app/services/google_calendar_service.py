"""
Google Calendar OAuth (read-only): each founder connects their OWN
Google account so CEO Briefing can reference their real upcoming
schedule, using the calendar.readonly scope specifically. Unlike
Stripe's Standard accounts (which only ever grant read_write regardless
of what's requested - confirmed the hard way in a prior session),
Google's OAuth genuinely honors a read-only scope grant at the provider
level: this integration is read-only by both application-level
discipline AND the token's actual granted scope. This code must never
call any Calendar API endpoint that creates, updates, or deletes an
event - only calendars.get and events.list, both read-only.

No Google client library (google-auth / google-api-python-client) is
used - Google's OAuth2 token endpoint and the Calendar v3 REST API are
both simple enough (a handful of POST/GET calls) that pulling in those
libraries' discovery-document machinery and dependency tree would be
disproportionate infrastructure for this. httpx (already a dependency)
is used directly instead, the same approach WebsiteScraperService
already uses for a different external HTTP integration in this app.

`access_type=offline` + `prompt=consent` on the authorize URL are both
required to guarantee Google actually returns a refresh_token - Google
only issues one on a user's FIRST-ever consent unless prompt=consent
forces the consent screen (and therefore a fresh grant) every time.

The OAuth `state` parameter is a short-lived, signed JWT (same pattern
as StripeService) carrying the business_id - not a DB row - so CSRF
protection doesn't depend on the founder's auth cookie surviving the
external redirect to and from Google.
"""
import secrets
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode
from uuid import UUID

import httpx
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import GoogleCalendarError, NotFoundError
from app.models.google_calendar_connection import GoogleCalendarConnection

_STATE_TOKEN_TYPE = "google_calendar_oauth_state"
_STATE_EXPIRE_MINUTES = 10
_SCOPE = "https://www.googleapis.com/auth/calendar.readonly"
_AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
_TOKEN_URL = "https://oauth2.googleapis.com/token"
_PRIMARY_CALENDAR_URL = "https://www.googleapis.com/calendar/v3/calendars/primary"
_EVENTS_URL = "https://www.googleapis.com/calendar/v3/calendars/primary/events"
_UPCOMING_DAYS = 7
_MAX_EVENTS = 50
_REQUEST_TIMEOUT_SECONDS = 10.0


class GoogleCalendarService:
    def __init__(self, db: Session):
        self.db = db

    def get_authorize_url(self, business_id: UUID) -> str:
        state = self._create_state_token(business_id)
        params = {
            "client_id": settings.GOOGLE_CALENDAR_CLIENT_ID,
            "redirect_uri": settings.GOOGLE_CALENDAR_OAUTH_REDIRECT_URI,
            "response_type": "code",
            "scope": _SCOPE,
            "access_type": "offline",
            "prompt": "consent",
            "state": state,
        }
        return f"{_AUTHORIZE_URL}?{urlencode(params)}"

    async def complete_oauth(self, code: str, state: str) -> GoogleCalendarConnection:
        """
        Exchanges an authorization code for tokens and stores the
        connection. Raises GoogleCalendarError with an honest, specific
        reason on any failure - an invalid/expired code, a missing
        refresh_token, or a Google API/network failure.
        """
        business_id = self._verify_state_token(state)

        async with httpx.AsyncClient(timeout=_REQUEST_TIMEOUT_SECONDS) as client:
            try:
                token_response = await client.post(
                    _TOKEN_URL,
                    data={
                        "code": code,
                        "client_id": settings.GOOGLE_CALENDAR_CLIENT_ID,
                        "client_secret": settings.GOOGLE_CALENDAR_CLIENT_SECRET,
                        "redirect_uri": settings.GOOGLE_CALENDAR_OAUTH_REDIRECT_URI,
                        "grant_type": "authorization_code",
                    },
                )
            except httpx.RequestError as exc:
                raise GoogleCalendarError("Could not reach Google to complete the connection.") from exc

        if not token_response.is_success:
            raise GoogleCalendarError(f"Google could not complete the connection: {token_response.text}")

        token_data = token_response.json()
        access_token = token_data.get("access_token")
        refresh_token = token_data.get("refresh_token")
        if not refresh_token:
            # Google only returns a refresh_token when it actually shows
            # the consent screen. access_type=offline + prompt=consent
            # above should guarantee this, but fail honestly rather than
            # store a connection with no way to renew access later.
            raise GoogleCalendarError(
                "Google did not return a long-lived connection. Please try connecting again."
            )

        google_email = await self._fetch_primary_calendar_email(access_token)

        connection = self._get_connection(business_id)
        if connection:
            connection.refresh_token = refresh_token
            connection.google_email = google_email
            connection.connected_at = datetime.now(timezone.utc)
        else:
            connection = GoogleCalendarConnection(
                business_id=business_id,
                refresh_token=refresh_token,
                google_email=google_email,
            )
        self.db.add(connection)
        self.db.commit()
        self.db.refresh(connection)
        return connection

    def get_status(self, business_id: UUID) -> dict:
        connection = self._get_connection(business_id)
        if not connection:
            return {"connected": False, "connected_at": None, "google_email": None}
        return {
            "connected": True,
            "connected_at": connection.connected_at,
            "google_email": connection.google_email,
        }

    def disconnect(self, business_id: UUID) -> None:
        connection = self._get_connection(business_id)
        if connection:
            self.db.delete(connection)
            self.db.commit()

    async def get_upcoming_events(self, business_id: UUID) -> list[dict]:
        """
        Fetches the next _UPCOMING_DAYS of events fresh from Google every
        call - nothing is cached or persisted, since calendar data
        changes frequently and a stored copy would just go stale.
        """
        connection = self._get_connection(business_id)
        if not connection:
            raise NotFoundError("Connect Google Calendar before fetching events.")

        access_token = await self._refresh_access_token(connection.refresh_token)

        now = datetime.now(timezone.utc)
        params = {
            "timeMin": now.isoformat(),
            "timeMax": (now + timedelta(days=_UPCOMING_DAYS)).isoformat(),
            "singleEvents": "true",
            "orderBy": "startTime",
            "maxResults": _MAX_EVENTS,
        }
        async with httpx.AsyncClient(timeout=_REQUEST_TIMEOUT_SECONDS) as client:
            try:
                response = await client.get(
                    _EVENTS_URL,
                    params=params,
                    headers={"Authorization": f"Bearer {access_token}"},
                )
            except httpx.RequestError as exc:
                raise GoogleCalendarError("Could not reach Google Calendar.") from exc

        if not response.is_success:
            raise GoogleCalendarError(f"Google Calendar returned an error: {response.text}")

        events = []
        for item in response.json().get("items", []):
            start = item.get("start", {})
            end = item.get("end", {})
            events.append(
                {
                    "title": item.get("summary") or "(No title)",
                    # All-day events carry a "date" (no time) instead of
                    # "dateTime" - fall back to that rather than drop them.
                    "start": start.get("dateTime") or start.get("date"),
                    "end": end.get("dateTime") or end.get("date"),
                }
            )
        return events

    async def _refresh_access_token(self, refresh_token: str) -> str:
        async with httpx.AsyncClient(timeout=_REQUEST_TIMEOUT_SECONDS) as client:
            try:
                response = await client.post(
                    _TOKEN_URL,
                    data={
                        "refresh_token": refresh_token,
                        "client_id": settings.GOOGLE_CALENDAR_CLIENT_ID,
                        "client_secret": settings.GOOGLE_CALENDAR_CLIENT_SECRET,
                        "grant_type": "refresh_token",
                    },
                )
            except httpx.RequestError as exc:
                raise GoogleCalendarError("Could not reach Google to refresh the connection.") from exc

        if not response.is_success:
            # Most commonly: the founder revoked access from their Google
            # account settings, outside this app entirely - the refresh
            # token is now permanently dead, and the honest fix is to
            # reconnect, not retry.
            raise GoogleCalendarError("Google Calendar access has expired or was revoked. Please reconnect.")
        return response.json()["access_token"]

    async def _fetch_primary_calendar_email(self, access_token: str) -> str:
        # The primary calendar's own id is the connected account's email
        # address - well-established Calendar API behavior, used here
        # specifically so identifying the account never requires a
        # broader email/profile/openid scope beyond calendar.readonly.
        async with httpx.AsyncClient(timeout=_REQUEST_TIMEOUT_SECONDS) as client:
            try:
                response = await client.get(
                    _PRIMARY_CALENDAR_URL,
                    headers={"Authorization": f"Bearer {access_token}"},
                )
            except httpx.RequestError as exc:
                raise GoogleCalendarError("Could not confirm the connected Google account.") from exc

        if not response.is_success:
            raise GoogleCalendarError("Could not confirm the connected Google account.")
        return response.json()["id"]

    def _get_connection(self, business_id: UUID) -> GoogleCalendarConnection | None:
        return (
            self.db.query(GoogleCalendarConnection)
            .filter(GoogleCalendarConnection.business_id == business_id)
            .first()
        )

    def build_redirect_url(self, *, success: bool, message: str | None = None) -> str:
        params = {"tab": "ceo-briefing", "calendar": "connected" if success else "error"}
        if message:
            params["message"] = message
        return f"{settings.FRONTEND_URL}/workspace?{urlencode(params)}"

    def _create_state_token(self, business_id: UUID) -> str:
        payload = {
            "business_id": str(business_id),
            "nonce": secrets.token_urlsafe(16),
            "type": _STATE_TOKEN_TYPE,
            "exp": datetime.now(timezone.utc) + timedelta(minutes=_STATE_EXPIRE_MINUTES),
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    def _verify_state_token(self, state: str) -> UUID:
        try:
            payload = jwt.decode(state, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        except JWTError:
            raise GoogleCalendarError(
                "This Google Calendar connection link is invalid or has expired. Please try connecting again."
            )
        if payload.get("type") != _STATE_TOKEN_TYPE:
            raise GoogleCalendarError(
                "This Google Calendar connection link is invalid. Please try connecting again."
            )
        return UUID(payload["business_id"])
