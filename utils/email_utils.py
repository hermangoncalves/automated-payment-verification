import imaplib
from typing import Optional
from utils.config_loader import load_config

def connect_to_email(config: dict = None) -> Optional[imaplib.IMAP4_SSL]:
    """
    Connect to an IMAP email server using provided configuration.
    
    Args:
        config (dict, optional): Configuration dictionary. Id None, loads from config.yaml
        
    Returns:
        imaplib.IMAP4_SSL: Connected IMAP client object.
        
    Raises:
        imaplib.IMAP4.error: If connection or login fails
        ValueError: If config is invalid
    """
    if config is None:
        config = load_config()
        
    try:
        imap_server = config['email']['imap_server']
        username = config['email']['username']
        password = config['email']['password']
    except KeyError as e:
        raise ValueError(f"Missing required email config field: {e}")
    
    try:
        mail = imaplib.IMAP4_SSL(imap_server)
        mail.login(username, password)
        print(f"Connected to {imap_server} as {username}")
        return mail
    except imaplib.IMAP4.error as e:
        raise imaplib.IMAP4.error(f"IMAP connection failed: {e}")
    
    
def disconnect_from_email(mail: imaplib.IMAP4_SSL) -> None:
    """
    Safely disconnect from IMAP Server
    
    Argsaa:
        mail (imalip.IMAP4_SSL): Connected IMAP client object
    """
    if mail:
        mail.logout()
        print("Disconnected from IMAP Server")
        
        
if __name__ == "__main__":
    try:
        mail = connect_to_email()
        mail.select("INBOX")
        print("Inbox selected successfully")
        disconnect_from_email(mail)
    except Exception as e:
        print(f"Error: {e}")