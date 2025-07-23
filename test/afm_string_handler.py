"""
AFMTool1 - AFM String Handler
Programmiert die JSON-Tabelle so, dass die letzte befüllte Zeile 
als afm_string verfügbar ist mit JSON-String-Kodierung
"""

import json
from pathlib import Path

def get_afm_string():
    """
    Holt die letzte befüllte Zeile als afm_string
    mit JSON-String-Kodierung der Spalten
    
    Returns:
        str: JSON-String der letzten Zeile oder None
    """
    try:
        # cases.json laden
        with open("../data/cases.json", 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        cases = data.get('cases', [])
        
        if not cases:
            return None
        
        # Letzte befüllte Zeile
        last_case = cases[-1]
        
        # Als JSON-String kodieren
        afm_string = json.dumps(last_case, ensure_ascii=False)
        
        return afm_string
        
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Fehler beim Laden: {e}")
        return None

def get_afm_string_with_metadata():
    """
    Erweiterte Version mit zusätzlichen Metadaten
    
    Returns:
        dict: afm_string mit Index und Metadaten
    """
    try:
        with open("../data/cases.json", 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        cases = data.get('cases', [])
        
        if not cases:
            return None
        
        # Letzte Zeile und Index
        last_index = len(cases) - 1
        last_case = cases[-1]
        
        # JSON-String der Spalten
        afm_string = json.dumps(last_case, ensure_ascii=False)
        
        return {
            "afm_string": afm_string,
            "index": last_index,
            "total_cases": len(cases),
            "decoded": last_case  # Für Vergleich
        }
        
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Fehler beim Laden: {e}")
        return None

def decode_afm_string(afm_string):
    """
    Dekodiert einen afm_string zurück zu den ursprünglichen Spalten
    
    Args:
        afm_string (str): JSON-String kodierte Zeile
        
    Returns:
        dict: Dekodierte Spalten oder None
    """
    try:
        return json.loads(afm_string)
    except json.JSONDecodeError as e:
        print(f"Fehler beim Dekodieren: {e}")
        return None

def main():
    """Test der AFM String Funktionen"""
    print("=== AFMTool1 - AFM String Handler ===")
    
    # 1. Einfacher afm_string
    afm_string = get_afm_string()
    if afm_string:
        print(f"\n1. AFM String (letzte Zeile):")
        print(f"   {afm_string}")
    else:
        print("\n1. Kein AFM String verfügbar")
    
    # 2. Mit Metadaten
    afm_data = get_afm_string_with_metadata()
    if afm_data:
        print(f"\n2. AFM String mit Metadaten:")
        print(f"   Index: {afm_data['index']}")
        print(f"   Total Cases: {afm_data['total_cases']}")
        print(f"   AFM String: {afm_data['afm_string']}")
        
        # 3. Dekodierung testen
        decoded = decode_afm_string(afm_data['afm_string'])
        if decoded:
            print(f"\n3. Dekodiert:")
            print(f"   Quelle: {decoded.get('quelle', 'N/A')}")
            print(f"   Fundstellen: {decoded.get('fundstellen', 'N/A')}")
    
    print("\nAFM String Handler abgeschlossen!")

if __name__ == "__main__":
    main()
