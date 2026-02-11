import base64
import re
from datetime import datetime
from email.utils import parsedate_to_datetime
from urllib.parse import urlparse
from tags import derive_tags


URL_REGEX = re.compile(
    r"https?://[^\s<>()\"']+",
    re.IGNORECASE
)


def _get_header(headers, name):
    for h in headers:
        if h["name"].lower() == name.lower():
            return h["value"]
    return ""


def _decode_body(payload):
    if "parts" in payload:
        for part in payload["parts"]:
            if part["mimeType"] == "text/plain":
                data = part["body"].get("data")
                if data:
                    return base64.urlsafe_b64decode(data).decode("utf-8")
    else:
        data = payload["body"].get("data")
        if data:
            return base64.urlsafe_b64decode(data).decode("utf-8")

    return ""


def extract_links(text: str) -> list[str]:
    """
    Extract URLs from plain text email body.
    """
    return URL_REGEX.findall(text or "")

def root_domain(url: str) -> str:
    host = urlparse(url).netloc.lower()
    if host.startswith("www."):
        host = host[4:]
    return host.split(".")[0]

def normalize_subject(subject: str) -> str:
    """
    Make subject filesystem- and id-friendly.
    """
    return (
        subject.lower()
        .strip()
        .replace(" ", "-")
        .replace("/", "-")
    )


def parse_email(service, msg_id):
    if not isinstance(msg_id, str):
        raise TypeError(f"msg_id must be str, got {type(msg_id)}")
    """
    Returns a list of flat schema dicts (one per link).
    """
    msg = service.users().messages().get(
        userId="me",
        id=msg_id,
        format="full"
    ).execute()

    payload = msg["payload"]
    headers = payload["headers"]

    subject = _get_header(headers, "Subject") or "Untitled"
    sender = _get_header(headers, "From")
    date_header = _get_header(headers, "Date")

    try:
        received_at = parsedate_to_datetime(date_header).isoformat()
        date_part = received_at[:10]
    except Exception:
        received_at = datetime.utcnow().isoformat()
        date_part = received_at[:10]

    body = _decode_body(payload).strip()
    links = extract_links(body)

    if not links:
        return []

    normalized_subject = normalize_subject(subject)

    items = []
    total = len(links)

    for index, url in enumerate(links, start=1):
        item = {
            "id": f"{date_part}-{normalized_subject}-{index}",
            "subject": subject if total == 1 else f"{subject} ({index}/{total})",
            "datetime": received_at,
            "url": url,
            "source": "email",
            "item": index,
            "tags": derive_tags(url),
            "from": sender,
        }
        items.append(item)

    return items
