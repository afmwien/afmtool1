"""
AFMTool1 - Einfacher AFM String Zugriff
Direkte Funktionen für afm_string Operationen
"""

import json

def get_afm_string_simple():
    """
    Einfachste Funktion: Letzte Zeile als afm_string
    """
    with open("../data/cases.json", 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    cases = data.get('cases', [])
    if cases:
        return json.dumps(cases[-1], ensure_ascii=False)
    return None

def print_afm_string():
    """
    Zeigt den aktuellen afm_string an
    """
    afm_string = get_afm_string_simple()
    if afm_string:
        print(f"AFM String: {afm_string}")
    else:
        print("Kein AFM String verfügbar")

if __name__ == "__main__":
    print("=== Einfacher AFM String Test ===")
    print_afm_string()
