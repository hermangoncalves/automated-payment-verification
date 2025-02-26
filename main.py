#!/home/herman/Projects/automated-payment-verification/venv/bin/python
import sys
from utils.notification import send_telegram_notification
from utils.config_loader import load_config, validate_config
from utils.email_utils import (
    connect_to_email, 
    disconnect_from_email, 
    fetch_emails, 
    parse_email_content, 
    mark_email_as_read
)

def main():
    try:
        config = load_config()
        validate_config(config)
        print("Payment Verification System initialized")

        # Connect, fetch, and parse emails
        mail = connect_to_email(config)
        emails = fetch_emails(mail, config)
        for email_data in emails:
            details = parse_email_content(email_data, config)
            print(f"Email ID: {email_data['id']}, Details: {details}")
            if details:  # Mark as read only if successfully parsed
                send_telegram_notification(config, details)
                mark_email_as_read(mail, email_data["id"])

        print(f"IMAP Server: {config['email']['imap_server']}")
        print(f"Running with Python: {sys.version}")
        
        disconnect_from_email(mail)
    except Exception as e:
        print(f"Failed to initialize: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()