# generate_views.py
from pathlib import Path
from datetime import datetime

VAULT = Path("vault")
INBOX = VAULT / "inbox"
VIEWS = VAULT / "docs"

def parse_filename(path):
    name = path.stem
    ts, slug = name.split("__", 1)

    date_part, time_part = ts.split("T")
    time_part = time_part.replace("-", ":", 2)

    dt = datetime.fromisoformat(f"{date_part}T{time_part}")
    return dt, slug, path.name


def generate_index():
    entries = []

    for md in INBOX.glob("*.md"):
        dt, slug, filename = parse_filename(md)
        entries.append((dt, slug, filename))

    # newest first
    entries.sort(key=lambda x: x[0], reverse=True)

    VIEWS.mkdir(exist_ok=True)

    out = VIEWS / "index.md"
    with out.open("w", encoding="utf-8") as f:
        f.write("# Inbox (latest first)\n\n")
        for dt, slug, filename in entries:
            f.write(
                f"- **{dt.strftime('%Y-%m-%d %H:%M')}** — "
                f"[{slug}](../inbox/{filename})\n"
            )

    print(f"Generated {out}")


if __name__ == "__main__":
    generate_index()

