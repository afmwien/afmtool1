"""
Database-Funktionen für AFMTool1
"""
import json
import os

DATABASE_PATH = "data/persones.json"

def load_database():
    """JSON-Datenbank laden"""
    if os.path.exists(DATABASE_PATH):
        with open(DATABASE_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"persones": []}

def save_database(data):
    """JSON-Datenbank speichern"""
    with open(DATABASE_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def add_person(quelle, fundstellen):
    """Person hinzufügen"""
    data = load_database()
    person = {
        "quelle": quelle,
        "fundstellen": fundstellen
    }
    data["persones"].append(person)
    save_database(data)
    return person
