"""
AFMTool1 - Einfache Abfrage der letzten Zeile
Direkter Code ohne LastColumnProcessor
"""

import json
from pathlib import Path

def get_last_row_column1_simple():
    """
    Einfache Abfrage: Spalte 1 (quelle) der letzten Zeile
    Ohne externe Klassen oder komplexe Verarbeitung
    """
    try:
        # Direkt cases.json laden
        with open("../data/cases.json", 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        cases = data.get('cases', [])
        
        if cases:
            # Letzter Eintrag [-1]
            last_case = cases[-1]
            return last_case.get('quelle', None)
        else:
            return None
            
    except FileNotFoundError:
        print("Fehler: cases.json nicht gefunden")
        return None
    except json.JSONDecodeError:
        print("Fehler: Ungültiges JSON Format")
        return None

def get_last_row_column2_simple():
    """
    Einfache Abfrage: Spalte 2 (fundstellen) der letzten Zeile
    """
    try:
        with open("../data/cases.json", 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        cases = data.get('cases', [])
        
        if cases:
            last_case = cases[-1]
            return last_case.get('fundstellen', None)
        else:
            return None
            
    except FileNotFoundError:
        print("Fehler: cases.json nicht gefunden")
        return None
    except json.JSONDecodeError:
        print("Fehler: Ungültiges JSON Format")
        return None

def get_last_row_both_simple():
    """
    Beide Spalten der letzten Zeile in einem Aufruf
    """
    try:
        with open("../data/cases.json", 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        cases = data.get('cases', [])
        
        if cases:
            last_case = cases[-1]
            return {
                "quelle": last_case.get('quelle', None),
                "fundstellen": last_case.get('fundstellen', None),
                "index": len(cases) - 1
            }
        else:
            return None
            
    except FileNotFoundError:
        print("Fehler: cases.json nicht gefunden")
        return None
    except json.JSONDecodeError:
        print("Fehler: Ungültiges JSON Format")
        return None

def main():
    """Terminal Test der einfachen Funktionen"""
    print("=== AFMTool1 - Einfache Letzte Zeile Abfrage ===")
    
    # Spalte 1
    spalte1 = get_last_row_column1_simple()
    print(f"\nSpalte 1 (quelle):")
    print(f"   {spalte1}")
    
    # Spalte 2  
    spalte2 = get_last_row_column2_simple()
    print(f"\nSpalte 2 (fundstellen):")
    print(f"   {spalte2}")
    
    # Beide zusammen
    both = get_last_row_both_simple()
    if both:
        print(f"\nBeide Spalten (Index {both['index']}):")
        print(f"   Quelle: {both['quelle']}")
        print(f"   Fundstellen: {both['fundstellen']}")
    else:
        print("\nKeine Daten gefunden")

if __name__ == "__main__":
    main()
