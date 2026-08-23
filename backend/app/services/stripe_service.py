"""
Stripe Connect OAuth: each founder connects their OWN existing Stripe
account (Standard - see security notes below) so LuminOS can read
their real transaction history automatically instead of requiring
manual revenue entry. LuminOS never processes payments, never holds
funds, and never creates charges on a founder's behalf - this is meant
to be read-only visibility into revenue that already exists on the
founder's own account ("your merchants collect payments directly").

This platform's Connect configuration does not honor scope=read_only
at the OAuth level (Stripe rejects it outright for this platform), so
the resulting access_token is technically read_write-capable - see
get_authorize_url and the comment on sync_transactions. The read-only
guarantee above is therefore an application-level discipline enforced
by this file only ever calling list/retrieve endpoints, not a property
of the token itself.

The OAuth `state` parameter is a short-lived, signed JWT (same
SECRET_KEY/algorithm as this app's own auth tokens, see
app.core.security) carrying the business_id - not a DB row - so CSRF
protection doesn't depend on the founder's auth cookie surviving the
external redirect to and from Stripe, only on the state value itself
being unguessable and verifiable when Stripe redirects back.
"""
import secrets
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode
from uuid import UUID

import stripe
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import NotFoundError, StripeConnectError
from app.models.revenue_entry import RevenueEntry, RevenueEntryOrigin
from app.models.stripe_connection import StripeConnection

_STATE_TOKEN_TYPE = "stripe_oauth_state"
_STATE_EXPIRE_MINUTES = 10
# A single bounded page of most recent charges per sync - "recent
# transactions", not a full historical backfill, so a sync can never
# run away pulling a founder's entire charge history in one call.
_SYNC_PAGE_SIZE = 100


class StripeService:
    def __init__(self, db: Session):
        self.db = db

    def get_authorize_url(self, business_id: UUID) -> str:
        state = self._create_state_token(business_id)
        return stripe.OAuth.authorize_url(
            client_id=settings.STRIPE_CONNECT_CLIENT_ID,
            redirect_uri=settings.STRIPE_OAUTH_REDIRECT_URI,
            response_type="code",
            # This platform's Connect configuration rejects scope=read_only
            # outright ("Please use the `read_write` scope...") - confirmed
            # against a real authorize attempt, not assumed. read_write is
            # what Stripe actually issues here; LuminOS's read-only
            # guarantee is therefore enforced at the APPLICATION level, not
            # the OAuth grant level - see the comment on sync_transactions
            # below, where the resulting token is actually used.
            scope="read_write",
            state=state,
        )

    async def complete_oauth(self, code: str, state: str) -> StripeConnection:
        """
        Exchanges an authorization code for an access token and stores
        the connection. Raises StripeConnectError with an honest,
        specific reason on any failure - an invalid/expired code, an
        invalid state, or a Stripe API/network failure.
        """
        business_id = self._verify_state_token(state)

        try:
            token = stripe.OAuth.token(
                api_key=settings.STRIPE_SECRET_KEY,
                grant_type="authorization_code",
                code=code,
            )
        except stripe.StripeError as exc:
            raise StripeConnectError(f"Stripe could not complete the connection: {exc}") from exc

        connection = self._get_connection(business_id)
        if connection:
            connection.stripe_account_id = token.stripe_user_id
            connection.access_token = token.access_token
            connection.connected_at = datetime.now(timezone.utc)
        else:
            connection = StripeConnection(
                business_id=business_id,
                stripe_account_id=token.stripe_user_id,
                access_token=token.access_token,
            )
        self.db.add(connection)
        self.db.commit()
        self.db.refresh(connection)
        return connection

    def get_status(self, business_id: UUID) -> dict:
        connection = self._get_connection(business_id)
        if not connection:
            return {"connected": False, "connected_at": None, "stripe_account_id": None}
        return {
            "connected": True,
            "connected_at": connection.connected_at,
            "stripe_account_id": connection.stripe_account_id,
        }

    async def sync_transactions(self, business_id: UUID) -> dict:
        connection = self._get_connection(business_id)
        if not connection:
            raise NotFoundError("Connect Stripe before syncing.")

        # NOTE: this token was granted with scope=read_write (Stripe's
        # Connect configuration for this platform does not honor
        # read_only - see get_authorize_url above), so it technically
        # CAN create/update/delete resources on the founder's connected
        # account. LuminOS's read-only promise is enforced here, in code,
        # not by the token itself: this client must only ever call
        # list/retrieve endpoints. Never call charges.create, refunds.*,
        # transfers.*, payouts.*, or any other write/create/update/delete
        # Stripe endpoint through this client, anywhere in this app.
        client = stripe.StripeClient(api_key=connection.access_token)
        try:
            charges = client.v1.charges.list(params={"limit": _SYNC_PAGE_SIZE})
        except stripe.StripeError as exc:
            raise StripeConnectError(f"Could not sync transactions from Stripe: {exc}") from exc

        existing_ids = {
            row[0]
            for row in self.db.query(RevenueEntry.stripe_charge_id)
            .filter(
                RevenueEntry.business_id == business_id,
                RevenueEntry.stripe_charge_id.isnot(None),
            )
            .all()
        }

        synced_count = 0
        for charge in charges.data:
            if charge.id in existing_ids:
                continue
            # Only real, settled revenue - not failed, pending, or
            # refunded charges - counts as income actually received.
            if not charge.paid or charge.refunded or charge.status != "succeeded":
                continue
            entry = RevenueEntry(
                business_id=business_id,
                amount=charge.amount / 100,
                currency=charge.currency.upper(),
                source=charge.description,
                entry_date=datetime.fromtimestamp(charge.created, tz=timezone.utc).date(),
                origin=RevenueEntryOrigin.STRIPE,
                stripe_charge_id=charge.id,
            )
            self.db.add(entry)
            synced_count += 1

        self.db.commit()
        return {"synced_count": synced_count, "total_fetched": len(charges.data)}

    def build_redirect_url(self, *, success: bool, message: str | None = None) -> str:
        params = {"tab": "revenue", "stripe": "connected" if success else "error"}
        if message:
            params["message"] = message
        return f"{settings.FRONTEND_URL}/workspace?{urlencode(params)}"

    def _get_connection(self, business_id: UUID) -> StripeConnection | None:
        return (
            self.db.query(StripeConnection)
            .filter(StripeConnection.business_id == business_id)
            .first()
        )

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
            raise StripeConnectError(
                "This Stripe connection link is invalid or has expired. Please try connecting again."
            )
        if payload.get("type") != _STATE_TOKEN_TYPE:
            raise StripeConnectError("This Stripe connection link is invalid. Please try connecting again.")
        return UUID(payload["business_id"])
