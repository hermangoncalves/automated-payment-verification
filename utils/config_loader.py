import yaml
import os
from typing import Dict, Any
import sys

def load_config(config_path: str = None) -> Dict[str, Any]:
    """
    Load configuration from a YAML file

    Args:
        config_path (str): Path to the config file.

    Returns:
        dict: Configuration data.
    
    Raises:
        FileNotFoundError: If the config file doesn't exist.
        yaml.YAMLError: If the YAML file is malformed
    # """
    if config_path is None:
        # Get the directory of this script (utils/)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Move up one level to the project root and into config/
        config_path = os.path.join(script_dir, "..", "config", "config.yaml")
    

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found at {config_path}")
    
    with open(config_path, 'r') as file:
        try:
            config = yaml.safe_load(file)
            return config
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Error parsing config file: {e}")
        
def validate_config(config: Dict[str, Any]) -> None:
    """
    Validate required fields in the configuration.

    Args:
        config (dict): Loaded configuration data.

    Raises:
        KeyError: If required fields are missing
    """
    required_section = [
        'email',
        'google_sheets',
        'parsing_rules',
        'notifications',
    ]

    for section in required_section:
        if section not in config or not config[section]:
            raise KeyError(f"Missing or empty section '{section}' in config")
    
    email_fields = ['imap_server', 'username', 'password']
    for field in email_fields:
        if field not in config['email'] or not config['email'][field]:
            raise KeyError(f"Missing or empty field '{field}' in email config")
        
    # TODO: Add more validation as needed (e.g., google_sheets, notifications)
    
    
if __name__ == "__main__":
    try:
        config  = load_config()
        validate_config(config)
        print("Configuration loaded and validated sucessfullt!")
        print(config)
    except Exception as e:
        print(f"Error: {e}")
