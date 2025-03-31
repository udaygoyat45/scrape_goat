import json
import os

def read_proxies():
    with open("proxies.txt") as fin:
        proxies = [x.strip() for x in fin.readlines()]
        return proxies

def load_processed_authors(filename="suspension_data.json"):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return {}
    return {}

def save_processed_authors(data, filename="suspension_data.json"):
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)