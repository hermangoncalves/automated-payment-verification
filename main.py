import sys
from utils.config_loader import load_config, validate_config
from utils.email_utils import connect_to_email, disconnect_from_email

def main():
    try:
        config = load_config()
        validate_config(config=config)
        print("Payment Verification System initialized")
        
        # Test IMAP connection
        mail = connect_to_email(config)
        mail.select("INBOX")  # Select inbox to ensure connection works
        print(f"IMAP Server: {config['email']['imap_server']}")
        print(f"Running with Python: {sys.version}")
        
        # Clean up
        disconnect_from_email(mail)
    except Exception as e:
        print(f"Failed to initialize: {e}")

if __name__ == "__main__":
    main()