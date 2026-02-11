from pathlib import Path
import yaml

INBOX_DIR = Path("vault/inbox")

def write_markdown(item: dict):
    INBOX_DIR.mkdir(parents=True, exist_ok=True)

    filename = f"{item['id']}.md"
    path = INBOX_DIR / filename

    frontmatter = {
        "id": item.get("id"),
        "subject": item.get("subject"),
        "datetime": item.get("datetime"),
        "url": item.get("url"),
        "source": item.get("source"),
        "item": item.get("item"),
        "tags": item.get("tags", []),
        "from": item.get("from"),
    }

    with open(path, "w", encoding="utf-8") as f:
        f.write("---\n")
        yaml.safe_dump(
            frontmatter,
            f,
            sort_keys=False,
            allow_unicode=True
        )
        f.write("---\n\n")

        if item.get("subject"):
            f.write(f"# {item['subject']}\n\n")

        if item.get("url"):
            f.write(f"{item['url']}\n")
