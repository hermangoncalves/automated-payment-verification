import imaplib
import email
from email.header import decode_header
from typing import Optional, List, Dict, Any
from utils.config_loader import load_config
from datetime import datetime, timedelta
import time
import sys

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
        
def fetch_emails(mail: imaplib.IMAP4_SSL, config: dict) -> List[Dict[str, Any]]:
    """
    Fetch and filter emails from the IMAP server based on config criteria.
    
    Args:
        mail (imaplib.IMAP4_SSL): Connected IMAP client.
        config (dict): Configuration with filtering rules.
    
    Returns:
        List[Dict]: List of filtered emails with metadata and content.
    
    Raises:
        imaplib.IMAP4.error: If email fetching fails.
    """
    mail.select("INBOX")
    fetch_unread = config.get('filtering', {}).get('fetch_unread_only', False)
    time_window = config.get('filtering', {}).get('time_window_minutes', None)
    
    if time_window:
        since_date = (datetime.now() - timedelta(minutes=time_window)).strftime("%d-%b-%Y")
        search_criteria = f'SINCE {since_date}'
    else:
        search_criteria = 'UNSEEN' if fetch_unread else 'ALL'
        
    status, email_ids = mail.search(None, search_criteria)
    if status != 'OK':
        raise imaplib.IMAP4.error("Failed to search emails")

    email_ids = email_ids[0].split()
    if not email_ids:
        print("No emails found matching criteria")
        return []
    
    subject_keywords = config.get('filtering', {}).get('subject_keywords', [])
    sender_domains = config.get('filtering', {}).get('sender_domains', [])
    
    filtered_emails = []
    
    for email_id in email_ids:
        status, msg_data = mail.fetch(email_id, "(RFC822)") #  padrão para mensagens de e-mail (incluindo cabeçalhos e corpo).
        if status != 'OK':
            continue
        
        raw_email = msg_data[0][1]
        email_message = email.message_from_bytes(raw_email)
        
        
        subject, encoding = decode_header(email_message["Subject"])[0]
        subject = subject.decode(encoding or "utf-8") if isinstance(subject, bytes) else subject
        sender = email_message.get("From", "")
        
        matches_subject = any(keyword.lower() in subject.lower() for keyword in subject_keywords) if subject_keywords else True
        matches_sender = any(domain.lower() in sender.lower() for domain in sender_domains) if sender_domains else True
        
        
        if matches_subject and matches_sender:
            filtered_emails.append({
                "id": email_id.decode(),
                "subject": subject,
                "sender": sender,
                "raw_content": raw_email # Store raw email for parsing later
            })
            
    print(f"Found {len(filtered_emails)} matching emails")
    return filtered_emails
        
if __name__ == "__main__":
    # Test the filtering
    try:
        config = load_config()
        mail = connect_to_email(config)
        emails = fetch_emails(mail, config)
        for email_data in emails:
            print(f"ID: {email_data['id']}, Subject: {email_data['subject']}, Sender: {email_data['sender']}")
        disconnect_from_email(mail)
    except Exception as e:
        print(f"Error: {e}")