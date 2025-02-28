import requests
import json
import logging
from typing import Dict, Any
from datetime import datetime, timezone

logging.basicConfig(
    filename='/home/herman/Projects/email-payment-receipt-webhook/logs/cron.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def send_webhook_notification(config: Dict[str, Any], payment_details: Dict[str, Any]) -> bool:
    """
    Send payment details to a configured webhook URL via HTTP POST.
    
    Args:
        config (dict): Configuration with webhook URL.
        payment_details (dict): Parsed payment details from email.
    
    Returns:
        bool: True if notification sent successfully, False otherwise.
    """
    
    webhook_config = config.get('notifications', {}).get('webhook', {})
    url = webhook_config.get('url')
    secret = webhook_config.get('secret')

    if not url:
        logger.warning("Webhook notification skipped: URL not configured in config.yaml")
        return False
    
    if not secret:
        logger.warning("Webhook notification skipped: Secret token not configured in config.yaml")
        return False
    
    payload = {
        "event": "payment_received",
        "data": payment_details,
        "timestamp": datetime.now(timezone.utc).isoformat() + "Z"
    }
    
    headers = {
        "Content-Type": "application/json",
        "X-Webhook-Secret": secret
    }
    try:
        
        response = requests.post(
            url,
            data=json.dumps(payload),
            headers=headers,
            timeout=10
        )
        
        response.raise_for_status()
        logger.info(f"Webhook notification sent for Transaction ID: {payment_details.get('transaction_id')}, Status: {response.status_code}")
        return True
    except requests.RequestException as e:
        logger.error(f"Failed to send webhook notification: {e}")
        return False
    

if __name__ == "__main__":
    # Test the webhook notification
    from utils.config_loader import load_config
    try:
        config = load_config()
        test_details = {
            "transaction_id": "566950604",
            "client_name": "ANIBAL ANDRADE BRITO",
            "amount_paid": "400,00 CVE",
            "payment_date": "2025-02-22",
            "description": "Netflix",
            "email_id": "17429",
            "sender": "BCA_Notificação <notification@bca.cv>",
            "subject": "Internet Banking | Extrato integrado"
        }
        success = send_webhook_notification(config, test_details)
        if success:
            print("Test webhook sent successfully")
        else:
            print("Test webhook failed")
    except Exception as e:
        print(f"Error during test: {e}")