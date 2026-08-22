"""
Fetches a founder's real, live website and extracts its visible text so
it can be written into memory_records as real, attributed site content
- see MemorySource.SCRAPED_SITE_CONTENT.

Deliberately a single HTTP GET with a hard timeout plus the standard
library's own HTML parser, not a headless browser or bypass of any
kind: this only needs to read a real marketing site's own content, and
a site blocking automated access (robots.txt, a 403, a WAF) is a
legitimate, honestly-reported failure - never something to work around.
"""
import re
import urllib.robotparser as robotparser
from urllib.parse import urlparse

import httpx
from html.parser import HTMLParser

from app.core.exceptions import WebsiteUnreachableError

USER_AGENT = "LuminOS-WebsiteBrief/1.0 (+https://luminos.app)"
REQUEST_TIMEOUT_SECONDS = 10.0
ROBOTS_TIMEOUT_SECONDS = 5.0
MAX_RESPONSE_BYTES = 5_000_000
MAX_CONTENT_CHARS = 4000

_SKIP_TAGS = {"script", "style", "noscript", "nav", "footer", "header", "svg", "template"}


class _VisibleTextExtractor(HTMLParser):
    """Collects text outside script/style/nav/footer/header markup."""

    def __init__(self):
        super().__init__()
        self._skip_depth = 0
        self.chunks: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag in _SKIP_TAGS:
            self._skip_depth += 1

    def handle_endtag(self, tag):
        if tag in _SKIP_TAGS and self._skip_depth > 0:
            self._skip_depth -= 1

    def handle_data(self, data):
        if self._skip_depth == 0:
            stripped = data.strip()
            if stripped:
                self.chunks.append(stripped)


class WebsiteScraperService:
    async def scrape(self, url: str) -> str:
        """
        Returns the page's extracted visible text (capped to
        MAX_CONTENT_CHARS), or raises WebsiteUnreachableError with an
        honest, specific reason - never a guess at what the site might
        contain.
        """
        if not await self._allowed_by_robots(url):
            raise WebsiteUnreachableError(
                "This site's robots.txt disallows automated access to this page."
            )

        try:
            async with httpx.AsyncClient(
                timeout=REQUEST_TIMEOUT_SECONDS, follow_redirects=True
            ) as client:
                response = await client.get(url, headers={"User-Agent": USER_AGENT})
        except httpx.TimeoutException:
            raise WebsiteUnreachableError("This site took too long to respond.")
        except httpx.RequestError:
            raise WebsiteUnreachableError("This site could not be reached.")

        if response.status_code == 403:
            raise WebsiteUnreachableError("This site appears to block automated access (HTTP 403).")
        if not response.is_success:
            raise WebsiteUnreachableError(f"This site returned an error (HTTP {response.status_code}).")

        content_length = response.headers.get("content-length")
        if content_length and int(content_length) > MAX_RESPONSE_BYTES:
            raise WebsiteUnreachableError("This page was too large to process.")

        content_type = response.headers.get("content-type", "")
        if "html" not in content_type.lower():
            raise WebsiteUnreachableError("This site did not return a readable HTML page.")

        extractor = _VisibleTextExtractor()
        extractor.feed(response.text)

        text = re.sub(r"\s+", " ", " ".join(extractor.chunks)).strip()
        if not text:
            raise WebsiteUnreachableError("No readable text content was found on this page.")

        return text[:MAX_CONTENT_CHARS]

    async def _allowed_by_robots(self, url: str) -> bool:
        parsed = urlparse(url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        try:
            async with httpx.AsyncClient(timeout=ROBOTS_TIMEOUT_SECONDS) as client:
                response = await client.get(robots_url, headers={"User-Agent": USER_AGENT})
        except httpx.RequestError:
            # No reachable robots.txt - the standard convention is to
            # treat this as permissive rather than block a real site.
            return True

        if not response.is_success:
            return True

        parser = robotparser.RobotFileParser()
        parser.parse(response.text.splitlines())
        return parser.can_fetch(USER_AGENT, url)
