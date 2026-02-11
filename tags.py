# tags.py
from urllib.parse import urlparse


def root_domain(url: str) -> str | None:
    """
    Extract a stable, human-readable root domain tag.
    Examples:
      https://www.youtube.com/watch?v=... → youtube
      https://substack.com/...            → substack
    """
    if not url:
        return None

    host = urlparse(url).netloc.lower()

    if not host:
        return None

    if host.startswith("www."):
        host = host[4:]

    return host.split(".")[0]


def derive_tags(url: str, existing: list[str] | None = None) -> list[str]:
    """
    Merge auto-derived tags with existing user tags.
    """
    tags = list(existing or [])

    domain = root_domain(url)
    if domain and domain not in tags:
        tags.append(domain)

    return tags
