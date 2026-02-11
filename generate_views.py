# generate_views.py
from pathlib import Path
from datetime import datetime
import markdown

VAULT = Path("vault")
INBOX = VAULT / "inbox"
VIEWS =  Path("docs")
VIEWS.mkdir(exist_ok=True)


def generate_index():
    entries = []

    for md in INBOX.glob("*.md"):
        stat = md.stat()
        entries.append((stat.st_mtime, md.name))

    # newest first
    entries.sort(reverse=True)

    VIEWS.mkdir(exist_ok=True)

    out = VIEWS / "index.md"
    with out.open("w", encoding="utf-8") as f:
        f.write("# Bookmarks\n\n")
        for _, filename in entries:
            f.write(f"- {filename}\n")

    print(f"Generated {out}")

def render_index_html():
    md_path = VIEWS / "index.md"
    html_path = VIEWS / "index.html"

    with md_path.open(encoding="utf-8") as f:
        body = markdown.markdown(f.read(), extensions=["extra"])

    html = f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Bookmarks</title>
</head>
<body>
{body}
</body>
</html>
"""

    with html_path.open("w", encoding="utf-8") as f:
        f.write(html)

    print(f"Generated {html_path}")

def generate_docs():
    generate_index()
    render_index_html()


if __name__ == "__main__":
    generate_docs()
