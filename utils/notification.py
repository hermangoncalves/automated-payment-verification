import telebot
from typing import Dict, Any

def send_telegram_notification(config: Dict[str, Any], payment_details: Dict[str, Any]) -> None:
    """
    Send a Telegram notification with payment details.
    
    Args:
        config (dict): Configuration with Telegram credentials.
        payment_details (dict): Parsed payment details to send.
    """
    telegram_config = config.get("notifications", {}).get("telegram", {})
    bot_token = telegram_config.get("bot_token")
    chat_id = telegram_config.get("chat_id")
    
    if not bot_token or not chat_id:
        print("Telegram notification skipped: Bot token or chat ID missing in config")
        return
    
    # Format the message
    message = (
        "📢 *Novo Pagamento Recebido!*\n\n"
        f"🆔 *ID da Transação:* `{payment_details.get('transaction_id', 'N/A')}`\n"
        f"👤 *Cliente:* {payment_details.get('client_name', 'N/A')}\n"
        f"💰 *Valor:* `{payment_details.get('amount_paid', 'N/A')}` CVE\n"
        f"📅 *Data do Pagamento:* {payment_details.get('payment_date', 'N/A')}\n"
        f"📝 *Descrição:* {payment_details.get('description', 'N/A')}\n\n"
    )
    
    # Send the message
    try:
        bot = telebot.TeleBot(bot_token, parse_mode="Markdown")
        bot.send_message(chat_id=chat_id, text=message)
        print(f"Telegram notification sent for Transaction ID: {payment_details.get('transaction_id')}")
    except Exception as e:
        print(f"Failed to send Telegram notification: {e}")

if __name__ == "__main__":
    # Test the notification
    from utils.config_loader import load_config
    config = load_config()
    test_details = {
        "transaction_id": "566950604",
        "client_name": "ANIBAL ANDRADE BRITO",
        "amount_paid": "400,00 CVE",
        "payment_date": "2025-02-22",
        "description": "Netflix",
        "email_id": "17429",
        "sender": "=?UTF-8?Q?BCA_Notifica=C3=A7=C3=A3o?= <notification@bca.cv>",
        "subject": "Internet Banking | Extrato integrado"
    }
    send_telegram_notification(config, test_details)