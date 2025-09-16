import os
import json

DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "allowance.json")

DEFAULT_DATA = {
    "child_name": "My Child",
    "weekly_allowance": 10,
    "tasks": []
}

def load_data():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    if not os.path.exists(DATA_FILE):
        save_data(DEFAULT_DATA)
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)
