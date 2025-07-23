"""
Database-Funktionen für AFMTool1
"""
import json
import os
from .afm_utils import update_case_afm_string

DATABASE_PATH = "data/cases.json"

def load_database():
    """JSON-Datenbank laden"""
    if os.path.exists(DATABASE_PATH):
        with open(DATABASE_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"cases": []}

def save_database(data):
    """JSON-Datenbank speichern"""
    with open(DATABASE_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def add_case_with_fields(case_data):
    """
    Case mit beliebigen Feldern hinzufügen (vollständig modular)
    
    Args:
        case_data (dict): Case-Daten mit beliebigen Spalten
        
    Returns:
        dict: Hinzugefügter Case mit AFM String
    """
    data = load_database()
    
    # AFM String automatisch generieren für alle befüllten Spalten
    case_with_afm = update_case_afm_string(case_data.copy())
    
    data["cases"].append(case_with_afm)
    save_database(data)
    return case_with_afm

def get_last_filled_cases(count=1):
    """
    Letzte befüllte Cases aus der Datenbank abrufen
    
    Args:
        count (int): Anzahl der letzten Cases (1 = nur letzter, -1 = alle)
    
    Returns:
        list: Liste der letzten Cases oder leere Liste
    """
    data = load_database()
    cases = data.get('cases', [])
    
    if not cases:
        return []
    
    if count == -1:  # Alle Cases
        return cases
    elif count == 1:  # Nur letzter Case
        return [cases[-1]]
    else:  # Letzte N Cases
        return cases[-count:] if count <= len(cases) else cases

def get_cases_count():
    """Anzahl der Cases in der Datenbank"""
    data = load_database()
    return len(data.get('cases', []))

def get_latest_case_info():
    """Detaillierte Informationen über den neuesten Case"""
    data = load_database()
    cases = data.get('cases', [])
    
    if not cases:
        return {
            "exists": False,
            "total_count": 0,
            "latest": None,
            "latest_index": -1
        }
    
    return {
        "exists": True,
        "total_count": len(cases),
        "latest": cases[-1],
        "latest_index": len(cases) - 1
    }
