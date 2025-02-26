import sys
from utils.config_loader import load_config, validate_config
from utils.email_utils import connect_to_email, disconnect_from_email, fetch_emails, parse_email_content

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
            print(f"Email ID: {email_data['id']}, Subject: {email_data['subject']}")
            print(f"Parsed Details: {details}")

        print(f"IMAP Server: {config['email']['imap_server']}")
        print(f"Running with Python: {sys.version}")
        
        disconnect_from_email(mail)
    except Exception as e:
        print(f"Failed to initialize: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()