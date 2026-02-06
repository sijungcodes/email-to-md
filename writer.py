import os
import re
from datetime import datetime
from config import VAULT_DIR


INBOX_DIR = "inbox"


def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"\s+", "-", text)
    return text[:50] or "untitled"


def write_markdown(email):
    inbox_path = os.path.join(VAULT_DIR, INBOX_DIR)
    os.makedirs(inbox_path, exist_ok=True)

    timestamp = datetime.now().isoformat(timespec="seconds").replace(":", "-")
    subject = slugify(email.get("subject", "untitled"))

    filename = f"{timestamp}__{subject}.md"
    path = os.path.join(inbox_path, filename)

    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# {email.get('subject', 'Untitled')}\n\n")
        f.write(f"**From:** {email.get('from', '')}\n\n")
        f.write(f"**Captured:** {datetime.now().isoformat(timespec="microseconds").replace(":", "-")}\n\n")
        f.write("---\n\n")
        f.write(email.get("body", ""))
        f.write("\n")
