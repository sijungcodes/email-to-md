#!/usr/bin/env python3

import os
import re
from pathlib import Path
from urllib.parse import urlparse
from datetime import datetime
import yaml


# ======================
# CONFIG
# ======================

INPUT_DIR = Path("vault/inbox")
OUTPUT_FILE = Path("docs/index.html")


# ======================
# UTILITIES
# ======================

def extract_frontmatter(content: str) -> dict:
    lines = content.splitlines()

    if not lines or lines[0].strip() != "---":
        return {}

    yaml_lines = []
    for line in lines[1:]:
        if line.strip() == "---":
            break
        yaml_lines.append(line)

    yaml_content = "\n".join(yaml_lines)

    try:
        return yaml.safe_load(yaml_content) or {}
    except Exception as e:
        print("YAML ERROR:", e)
        print(yaml_content)
        return {}


def extract_domain(url: str) -> str:
    """
    Extract clean domain from URL.
    """
    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    return domain.replace("www.", "")


def format_datetime(dt_str: str) -> tuple:
    """
    Parse ISO datetime string and return:
    - datetime object
    - formatted display string
    """
    print("Parsing datetime:", dt_str)
    dt = datetime.fromisoformat(dt_str)
    display = dt.strftime("%Y-%m-%d %H:%M")
    return dt, display


# ======================
# CORE LOGIC
# ======================

def load_items():
    items = []
    
    for file in INPUT_DIR.glob("*.md"):
        content = file.read_text(encoding="utf-8")
        meta = extract_frontmatter(content)
        
        if not meta:
            continue

        if "url" not in meta or "subject" not in meta:
            continue

        dt_obj, dt_display = format_datetime(meta["datetime"])

        item = {
            "title": meta["subject"],
            "url": meta["url"],
            "domain": extract_domain(meta["url"]),
            "datetime": dt_obj,
            "datetime_display": dt_display,
            "tags": meta.get("tags", []),
            "source": meta.get("source", ""),
            "details_path": file.name,
        }

        items.append(item)

    # Sort newest first
    items.sort(key=lambda x: x["datetime"], reverse=True)

    return items


def render_html(items):
    entries = []

    for item in items:
        entries.append(f"""
        <article class="entry">
            <h2 class="title">
                <a href="{item['url']}" target="_blank">
                    {item['title']}
                </a>
            </h2>
            <div class="meta">
                {item['domain']} · {item['datetime_display']} · {item['source']} · 
                <a href="{item['details_path']}">details</a>
            </div>
        </article>
        """)

    return f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Inbox</title>

<style>
body {{
    margin: 0;
    padding: 0;
    background: #ffffff;
    color: #222;
    font-family: Georgia, "Times New Roman", serif;
    line-height: 1.6;
}}

.container {{
    max-width: 680px;
    margin: 60px auto;
    padding: 0 20px;
}}

header {{
    font-size: 14px;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: #888;
    margin-bottom: 40px;
}}

.entry {{
    margin-bottom: 48px;
}}

.title {{
    font-size: 22px;
    font-weight: normal;
    margin: 0 0 6px 0;
}}

.title a {{
    text-decoration: none;
    color: #000;
}}

.title a:hover {{
    text-decoration: underline;
}}

.meta {{
    font-size: 13px;
    color: #888;
}}

.meta a {{
    color: #888;
    text-decoration: none;
}}

.meta a:hover {{
    text-decoration: underline;
}}
</style>

</head>
<body>
<div class="container">

<header>Inbox</header>

{''.join(entries)}

</div>
</body>
</html>
"""


def main():
    items = load_items()

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(render_html(items), encoding="utf-8")

    print(f"Generated index with {len(items)} items → {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
