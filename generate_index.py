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
    rows = []

    for i, item in enumerate(items, start=1):
        rows.append(f"""
        <tr>
            <td class="rank">{i}.</td>
            <td class="title">
                <a href="{item['url']}" target="_blank">{item['title']}</a>
                <span class="domain">({item['domain']})</span>
                <div class="meta">
                    {item['datetime_display']} • {item['source']} • 
                    <a href="{item['details_path']}">details</a>
                </div>
            </td>
        </tr>
        """)

    return f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Inbox</title>
<style>
body {{
    font-family: Verdana, Geneva, sans-serif;
    background: #f6f6ef;
    margin: 0;
}}
.header {{
    background: #ff6600;
    padding: 6px 10px;
    font-weight: bold;
}}
.container {{
    padding: 10px;
    max-width: 900px;
    margin: auto;
}}
.rank {{
    width: 30px;
    color: #828282;
    vertical-align: top;
}}
.title a {{
    text-decoration: none;
    color: black;
}}
.domain {{
    color: #828282;
    font-size: 12px;
}}
.meta {{
    font-size: 10px;
    color: #828282;
}}
.meta a {{
    color: #828282;
    text-decoration: none;
}}
</style>
</head>
<body>
<div class="header">Inbox</div>
<div class="container">
<table>
{''.join(rows)}
</table>
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
