import sys
from utils.config_loader import load_config, validate_config

def main():
    try:
        config = load_config()
        validate_config(config=config)
        print("Payment Verification System initialized")
        print(f"Running with Python: {sys.version}")
    except Exception as e:
        print(f"Failed to initialize: {e}")

if __name__ == "__main__":
    main()