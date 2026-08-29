"""
Thin wrapper around Resend for transactional email delivery - the only
file in this app that imports the `resend` SDK, same "one file owns the
third-party import" convention as openai_provider.py.

Email delivery is inherently less reliable than this app's own database
writes and must never be a single point of failure for a core feature:
send_email never raises. A missing RESEND_API_KEY (e.g. someone running
this app without configuring it) logs a clear warning and returns; an
actual send failure is caught and logged the same way. Either way, the
feature that triggered the email (password reset, an Opportunity Radar
notification) must complete exactly as if the email had never been
attempted.

Resend's unverified-account rate limit is 2 requests/second - _send
retries specifically on a 429 (resend.exceptions.RateLimitError), same
stop/backoff shape openai_provider.py already uses for OpenAI, so a
burst of Radar notifications has a real chance to succeed on retry
instead of just being dropped. Non-rate-limit failures (a bad API key,
a malformed address) are never retried - retrying those would only
delay an outcome that was never going to change.
"""
import resend
from resend.exceptions import RateLimitError
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class EmailService:
    def send_email(self, to: str, subject: str, html: str) -> dict | None:
        """
        Returns Resend's own send response (contains its "id") on success,
        or None on either a skipped or a failed send - callers that don't
        care can ignore the return value entirely (every caller in this
        app currently does); it exists so a caller that needs to confirm
        genuine delivery (e.g. via resend.Emails.get(id)) can.
        """
        if not settings.RESEND_API_KEY:
            logger.warning("RESEND_API_KEY is not configured - skipping email to %s (%r)", to, subject)
            return None

        resend.api_key = settings.RESEND_API_KEY
        try:
            return self._send(to, subject, html)
        except Exception as exc:  # noqa: BLE001 - a failed send must never crash the caller
            logger.error("Failed to send email to %s (%r): %s", to, subject, exc)
            return None

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        retry=retry_if_exception_type(RateLimitError),
    )
    def _send(self, to: str, subject: str, html: str) -> dict:
        return resend.Emails.send(
            {
                "from": settings.RESEND_FROM_EMAIL,
                "to": [to],
                "subject": subject,
                "html": html,
            }
        )
