from flask import Flask, request, jsonify
import logging
import os
from rich.logging import RichHandler


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

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route('/webhook', methods=['POST'])
def webhook():
    """
    Receive payment receipt notifications via POST request.
    Logs the payload and returns a success response.
    """
    try:
        payload = request.get_json()
        if not payload:
            logger.error('❌ No JSON payload received')
            return jsonify({'error': 'No JSON payload'}), 400
            
        logger.info(f'🔔 Received webhook payload: {payload}')
        return jsonify({"status": "success", "message": "Webhook received"}), 200
    
    except Exception as e:
        logger.error(f"⚠️ Error processing webhook: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    logger.info("🚀 Starting Flask webhook test server on http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)
