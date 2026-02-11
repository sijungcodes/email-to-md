import os
from datetime import datetime
from config import VAULT_DIR, DEFAULT_FILE


def write_markdown(email):
    os.makedirs(VAULT_DIR, exist_ok=True)

    path = os.path.join(VAULT_DIR, DEFAULT_FILE)

    with open(path, "a", encoding="utf-8") as f:
        f.write("\n---\n\n")
        f.write(f"## {email['subject'] or 'Untitled'}\n")
        f.write(f"**From:** {email['from']}\n\n")
        f.write(f"**Date:** {datetime.now().isoformat()}\n\n")
        f.write(email["body"])
        f.write("\n")

