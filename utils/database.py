import pandas as pd
import os
from typing import List, Dict, Any


def load_client_database(db_path: str = None) -> List[Dict[str, Any]]:
    """
    Load the client database from a CSV file.

    Args:
        db_path (str, optional): Path to the CSV file. Defaults to database/clients.csv.

    Returns:
        List[Dict]: List of client records.

    Raises:
        FileNotFoundError: If the CSV file doesn't exist.
    """

    if db_path is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(script_dir, "..", "database", "clients.csv")

    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Client database not found at {db_path}")

    try:
        df = pd.read_csv(db_path)
        clients = df.to_dict(orient="records")
        print(f"Loaded {len(clients)} clients from database")
        return clients
    except Exception as e:
        raise Exception(f"Error loading clients database: {e}")


if __name__ == "__main__":
    try:
        clients = load_client_database()
        for client in clients:
            print(client)
    except Exception as e:
        print(f"Error: {e}")
