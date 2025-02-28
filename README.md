# Payment Receipt Webhook

## Overview
This project is a Python-based webhook that monitors an email inbox for payment receipt notifications, extracts payment details, and sends them to an external application via an HTTP POST request. It automates the process of notifying other systems (e.g., accounting software, CRM) whenever a payment is received, reducing manual effort and enabling real-time integration.

### Why This Project?
Manually tracking payment receipt emails and updating other systems is time-consuming. This webhook bridges the gap by:
- Fetching unread payment emails from an IMAP server (e.g., Gmail).
- Extracting details like transaction ID, amount, and client name.
- Notifying an external application instantly via a configurable webhook URL.

## Features
- **Email Monitoring**: Fetches unread emails every 5 minutes via cron.
- **Payment Extraction**: Parses email bodies (text/html) and attachments (PDFs) for payment details.
- **Webhook Notifications**: Sends JSON payloads to a specified URL.
- **Reliable Execution**: Runs as a scheduled cron job.

## Setup
1. **Clone the Repo**: `git clone https://github.com/hermangoncalves/email-payment-receipt-webhook.git`
2. **Setup Virtual Env**: `python3 -m venv venv && source venv/bin/activate`
3. **Install Dependencies**: `pip install -r requirements.txt`
4. **Configure**: Edit `config/config.yaml` with IMAP credentials and webhook URL.
5. **Run Cron**: Add `*/5 * * * * /path/to/venv/bin/python /path/to/main.py >> logs/cron.log 2>&1` to `crontab -e`.

## Usage
- Run manually: `python main.py`
- Check logs: `cat logs/cron.log`