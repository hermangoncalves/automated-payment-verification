import imaplib
import email
from email.header import decode_header
from typing import Optional, List, Dict, Any
from utils.config_loader import load_config
from datetime import datetime, timedelta
import PyPDF2
import re
import io
import sys

# TODO: refine filtering (e.g., mark emails as read, add more criteria).
# TODO: enhance connect_to_email with OAuth2 support or additional error logging.

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
    
    if time_window and fetch_unread:
        since_date = (datetime.now() - timedelta(minutes=time_window)).strftime("%d-%b-%Y")
        search_criteria = f'UNSEEN SINCE {since_date}'
    elif fetch_unread:
        search_criteria = 'UNSEEN'
    else:
        search_criteria = 'ALL' if not time_window else f'SINCE {(datetime.now() - timedelta(minutes=time_window)).strftime("%d-%b-%Y")}'
        
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


def parse_email_content(email_data: Dict[str, Any], config: dict) -> Dict[str, Any]:
    """
    Parse email content and attachments to extract payment details
    
    Args:
        email_data (dict): Email metadata and raw content from fetch_emails.
        config (dict): Configuration with parsing rules.
    
    Returns:
        dict: Extracted payment details or empty dict if parsing fails.
    """

    email_message = email.message_from_bytes(email_data['raw_content'])
    payment_details = {}
    
    sender = email_data["sender"].lower()
    parsing_rules = config.get("parsing_rules", {})
    for bank, rules in parsing_rules.items():
       if any(domain in sender for domain in config.get('filtering', {}).get('sender_domains', [])):
            bank_key = bank
            break
    if not bank_key:
        print(f"No parsing rules matched for sender: {sender}")
        return {}
        
    rules = parsing_rules.get(bank_key, {})
    
    for part in email_message.walk():
        content_type = part.get_content_type()
        if content_type == "application/octet-stream":
            # Assume it might be a PDF (common for unnamed attachments)            
            try:
                pdf_content = extract_pdf_content(part.get_payload(decode=True))
                payment_details.update(extract_details(pdf_content, rules))
            except Exception as e:
                print(e)
                print(f"Skipping unreadable octet-stream attachment for Email ID: {email_data['id']}")
    
    payment_details['email_id'] = email_data['id']
    payment_details['sender'] = email_data['sender']
    payment_details['subject'] = email_data['subject']
    
    return payment_details if payment_details else {}
        
def extract_pdf_content(pdf_data: bytes) -> str:
    """
    Extract text from a PDF attachment.
    
    Args:
        pdf_data (bytes): Raw PDF content.
    
    Returns:
        str: Extracted text.
    """
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_data))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        print(f"Error extracting PDF content: {e}")
        return ""
    
def extract_details(content: str, rules: Dict[str, str]) -> Dict[str, Any]:
    """
    Extract payment details from text using regex rules.
    
    Args:
        content (str): Text content to parse.
        rules (dict): Regex patterns for each field.
    
    Returns:
        dict: Extracted details.
    """
    
    details = {}
    for field, pattern in rules.items():
        regex_pattern = rf"{pattern}\s*:\s*(.+)"
        match = re.search(regex_pattern, content)
        if match:
            details[field] = match.group(1).strip()
    return details


def mark_email_as_read(mail: imaplib.IMAP4_SSL, email_id: str) -> None:
    """
    Mark an email as read by setting the \Seen flag.
    
    Args:
        mail (imaplib.IMAP4_SSL): Connected IMAP client.
        email_id (str): Email ID to mark as read.
    """
    try:
        status, _ = mail.store(email_id, "+FLAGS", "\Seen")
        if status == "OK":
            print(f"Marked Email ID {email_id} as read")
        else:
            print(f"Failed to mark Email ID {email_id} as read")
    except imaplib.IMAP4.error as e:
        print(f"Error marking email as read: {e}")
        
if __name__ == "__main__":
    # Test the parsing
    try:
        config = load_config()
        mail = connect_to_email(config)
        emails = fetch_emails(mail, config)
        for email_data in emails:
            details = parse_email_content(email_data, config)
            print(f"Email ID: {email_data['id']}, Details: {details}")
        disconnect_from_email(mail)
    except Exception as e:
        print(f"Error: {e}")