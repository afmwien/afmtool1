"""
AFMTool1 - AFM String Auto-Generator
Generiert automatisch AFM Strings für alle Zeilen der cases.json
"""

import json
from pathlib import Path

def generate_afm_strings_for_all_cases():
    """
    Generiert AFM Strings für alle Cases automatisch
    Jede Zeile bekommt einen afm_string mit JSON-Kodierung der anderen Spalten
    """
    try:
        # cases.json laden
        with open("data/cases.json", 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        cases = data.get('cases', [])
        
        if not cases:
            print("Keine Cases gefunden!")
            return False
        
        # Für jeden Case AFM String generieren
        updated_cases = []
        for i, case in enumerate(cases):
            if isinstance(case, dict):
                # Nur die Hauptdaten für AFM String (ohne afm_string selbst)
                case_data = {k: v for k, v in case.items() if k != 'afm_string'}
                
                # JSON-String generieren
                afm_string = json.dumps(case_data, ensure_ascii=False)
                
                # AFM String zur Case hinzufügen
                updated_case = case.copy()
                updated_case['afm_string'] = afm_string
                updated_cases.append(updated_case)
                
                print(f"Case {i+1}: AFM String generiert")
            else:
                updated_cases.append(case)
        
        # Aktualisierte Daten speichern
        data['cases'] = updated_cases
        
        with open("data/cases.json", 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ AFM Strings für {len(updated_cases)} Cases generiert!")
        return True
        
    except Exception as e:
        print(f"❌ Fehler beim Generieren der AFM Strings: {e}")
        return False

def update_afm_string_for_case(case_index):
    """
    Aktualisiert den AFM String für einen spezifischen Case
    
    Args:
        case_index (int): Index des Cases (0-basiert)
    """
    try:
        with open("data/cases.json", 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        cases = data.get('cases', [])
        
        if case_index < 0 or case_index >= len(cases):
            print(f"❌ Ungültiger Case-Index: {case_index}")
            return False
        
        case = cases[case_index]
        if isinstance(case, dict):
            # Hauptdaten für AFM String (ohne afm_string selbst)
            case_data = {k: v for k, v in case.items() if k != 'afm_string'}
            
            # Neuen AFM String generieren
            afm_string = json.dumps(case_data, ensure_ascii=False)
            cases[case_index]['afm_string'] = afm_string
            
            # Speichern
            with open("data/cases.json", 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ AFM String für Case {case_index + 1} aktualisiert!")
            return True
        else:
            print(f"❌ Case {case_index + 1} ist kein gültiges Dictionary")
            return False
            
    except Exception as e:
        print(f"❌ Fehler beim Aktualisieren: {e}")
        return False

def show_all_afm_strings():
    """
    Zeigt alle AFM Strings in einer übersichtlichen Form
    """
    try:
        with open("data/cases.json", 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        cases = data.get('cases', [])
        
        print("=== Alle AFM Strings ===")
        for i, case in enumerate(cases):
            if isinstance(case, dict):
                quelle = case.get('quelle', 'Unbekannt')
                afm_string = case.get('afm_string', 'Nicht vorhanden')
                
                print(f"\nCase {i+1} ({quelle}):")
                print(f"  AFM String: {afm_string}")
                
                # AFM String dekodieren zur Verifikation
                try:
                    decoded = json.loads(afm_string)
                    print(f"  Dekodiert: {decoded}")
                except:
                    print(f"  ⚠️  AFM String konnte nicht dekodiert werden")
            else:
                print(f"\nCase {i+1}: Kein gültiges Dictionary")
        
        return True
        
    except Exception as e:
        print(f"❌ Fehler beim Anzeigen: {e}")
        return False

def main():
    """Test-Funktionen"""
    print("=== AFMTool1 - AFM String Auto-Generator ===")
    
    print("\n1. Alle AFM Strings generieren...")
    if generate_afm_strings_for_all_cases():
        print("\n2. AFM Strings anzeigen...")
        show_all_afm_strings()
        
        print("\n3. Test: AFM String für Case 1 aktualisieren...")
        update_afm_string_for_case(0)
    
    print("\nAFM String Auto-Generator abgeschlossen!")

if __name__ == "__main__":
    main()
