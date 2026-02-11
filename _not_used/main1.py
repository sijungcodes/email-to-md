import time
from gmail_client import (
    get_gmail_service,
    get_or_create_label,
    fetch_unprocessed_messages,
    mark_as_processed
)
from email_parser import parse_email
from writer import write_markdown
from config import POLL_INTERVAL


def main():
    service = get_gmail_service()
    label_id = get_or_create_label(service)

    print("Email-to-MD running...")

    while True:
        messages = fetch_unprocessed_messages(service)

        for msg in messages:
            try:
                email = parse_email(service, msg["id"])
                write_markdown(email)
                mark_as_processed(service, msg["id"], label_id)
                print("Processed:", email["subject"])

            except Exception as e:
                print("Error processing message:", e)

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
