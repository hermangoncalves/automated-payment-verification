#!/home/user/payment_verification/venv/bin/python
import sys
import os
import logging
from rich.logging import RichHandler
from utils.config_loader import load_config, validate_config
from utils.email_utils import connect_to_email, disconnect_from_email, fetch_emails, parse_email_content, mark_email_as_read
from utils.webhook import send_webhook_notification  # New import

log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(log_dir, "webhook.log")),
        RichHandler() 
    ]
)

logger = logging.getLogger(__name__)

def main():
    try:
        config = load_config()
        validate_config(config)
        logger.info("Payment Receipt Webhook initialized")

        # Connect to email server
        mail = connect_to_email(config)
        logger.info("Connected to IMAP server")

        # Fetch and process emails
        emails = fetch_emails(mail, config)
        if not emails:
            logger.info("No new payment receipt emails found")
        else:
            logger.info(f"Found {len(emails)} new payment receipt emails")
            for email_data in emails:
                details = parse_email_content(email_data, config)
                if details:
                    logger.info(f"Parsed payment details from Email ID {email_data['id']}: {details}")
                    send_webhook_notification(config, details)
                    mark_email_as_read(mail, email_data["id"])
                else:
                    logger.warning(f"Failed to parse payment details from Email ID {email_data['id']}")

        logger.info(f"IMAP Server: {config['email']['imap_server']}")
        logger.info(f"Python Version: {sys.version.split()[0]}")
        disconnect_from_email(mail)
        logger.info("Process completed successfully")

    except Exception as e:
        logger.error(f"Failed to process emails: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()