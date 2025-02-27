import logging
import sys
import time
import pyfiglet
from rich import print
from rich.logging import RichHandler
from rich.console import Console
from rich.table import Table
from rich.progress import track
from rich.panel import Panel
from utils.database import load_client_database
from utils.notification import send_telegram_notification
from utils.config_loader import load_config, validate_config
from utils.email_utils import (
    connect_to_email,
    disconnect_from_email,
    fetch_emails,
    parse_email_content,
    mark_email_as_read,
)

# Set up Rich logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)],
)
logger = logging.getLogger("rich")

console = Console()

def show_banner():
    """Display a cool ASCII banner"""
    banner = pyfiglet.figlet_format("PAYMENT BOT", font="slant")
    console.print(f"[bold cyan]{banner}[/bold cyan]")
    console.print(Panel("[bold yellow]🔍 Scanning Emails for Payment Verifications[/bold yellow]", expand=False))

def main():
    try:
        console.clear()
        show_banner()
        time.sleep(1)  # Just to let the banner shine for a moment
        
        config = load_config()
        validate_config(config)
        logger.info("✅ Configuration loaded successfully")

        clients = load_client_database()
        logger.info(f"📂 Client database loaded with [bold green]{len(clients)}[/bold green] records")

        # Connect to email
        mail = connect_to_email(config)
        logger.info("📧 Connected to email server")

        # Fetch and process emails with a progress bar
        emails = fetch_emails(mail, config)
        if not emails:
            console.print("[bold yellow]⚠️ No new emails found.[/bold yellow]")
        else:
            for email_data in track(emails, description="📩 Processing emails..."):
                details = parse_email_content(email_data, config)
                console.print(f"[bold yellow]📨 Email ID:[/bold yellow] {email_data['id']}, [bold cyan]Details:[/bold cyan] {details}")
                if details:
                    send_telegram_notification(config, details)
                    mark_email_as_read(mail, email_data["id"])
        
        # Display a summary table
        table = Table(title="[bold magenta]📊 System Information[/bold magenta]")
        table.add_column("Property", style="cyan", justify="left")
        table.add_column("Value", style="magenta", justify="right")
        table.add_row("IMAP Server", config["email"]["imap_server"])
        table.add_row("Python Version", sys.version.split()[0])
        console.print(table)

        disconnect_from_email(mail)
        logger.info("🎉 Process completed successfully! 🎉")

    except Exception as e:
        console.print(f"[bold red]❌ ERROR:[/bold red] {e}", style="red")
        sys.exit(1)

if __name__ == "__main__":
    main()
