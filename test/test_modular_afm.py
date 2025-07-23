"""
Test für modulare AFM String-Funktionalität
Testet ob ALLE befüllten Spalten erfasst werden
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.database import add_case_with_fields, load_database
from utils.afm_utils import validate_afm_strings
import json

def test_modular_afm_functionality():
    """Test der vollständig modularen AFM String-Funktionalität"""
    print("=== Test: Modulare AFM String-Funktionalität ===")
    
    # Test Case mit vielen verschiedenen Spalten
    test_case_1 = {
        "quelle": "Testregister Hamburg",
        "fundstellen": "TEST 456789, Datum 23.07.2025",
        "art": "Zivilrecht",
        "instanz": "Landgericht Hamburg",
        "aktenzeichen": "12 O 345/25",
        "datum": "2025-07-23",
        "status": "rechtskräftig",
        "anmerkung": "Vollständig modularer Test",
        "betrag": "15000 EUR",
        "partei_1": "Mustermann GmbH",
        "partei_2": "Testfirma AG"
    }
    
    print("\n1. Füge Test Case mit 11 Spalten hinzu...")
    try:
        result = add_case_with_fields(test_case_1)
        print("   ✅ Case erfolgreich hinzugefügt")
        
        # AFM String analysieren
        afm_string = result.get('afm_string', '')
        if afm_string:
            afm_data = json.loads(afm_string)
            print(f"   📊 AFM String enthält {len(afm_data)} Felder:")
            for key, value in afm_data.items():
                print(f"      - {key}: {value}")
        
    except Exception as e:
        print(f"   ❌ Fehler: {e}")
    
    # Test Case mit leeren/None Werten (sollten ignoriert werden)
    test_case_2 = {
        "quelle": "Testregister Berlin",
        "fundstellen": "BERLIN 999888",
        "kategorie": "Verwaltungsrecht",
        "leer_feld": "",  # Sollte ignoriert werden
        "none_feld": None,  # Sollte ignoriert werden
        "gueltig_feld": "Nur dieses ist gültig"
    }
    
    print("\n2. Füge Test Case mit leeren Feldern hinzu...")
    try:
        result = add_case_with_fields(test_case_2)
        print("   ✅ Case erfolgreich hinzugefügt")
        
        # AFM String analysieren
        afm_string = result.get('afm_string', '')
        if afm_string:
            afm_data = json.loads(afm_string)
            print(f"   📊 AFM String enthält {len(afm_data)} Felder (leere ignoriert):")
            for key, value in afm_data.items():
                print(f"      - {key}: {value}")
            
            # Prüfen ob leere Felder korrekt ignoriert wurden
            if 'leer_feld' not in afm_data and 'none_feld' not in afm_data:
                print("   ✅ Leere/None Felder wurden korrekt ignoriert")
            else:
                print("   ⚠️  Leere/None Felder wurden NICHT ignoriert!")
        
    except Exception as e:
        print(f"   ❌ Fehler: {e}")
    
    print("\n3. Validiere alle AFM Strings...")
    validation_results = validate_afm_strings()
    
    valid_cases = []
    invalid_cases = []
    
    for result in validation_results:
        if "error" not in result:
            if result["afm_valid"]:
                valid_cases.append(result)
            else:
                invalid_cases.append(result)
    
    print(f"   ✅ {len(valid_cases)} gültige AFM Strings")
    print(f"   ⚠️  {len(invalid_cases)} ungültige AFM Strings")
    
    if invalid_cases:
        print("\n   Ungültige Cases:")
        for case in invalid_cases:
            print(f"      - Case {case['case_index']+1} ({case['quelle']}): {case['missing_fields']}")
    
    print("\n4. Zeige Statistik der erfassten Spalten...")
    data = load_database()
    cases = data.get('cases', [])
    
    all_columns = set()
    for case in cases:
        if isinstance(case, dict):
            all_columns.update(case.keys())
    
    print(f"   📊 Insgesamt {len(all_columns)} verschiedene Spalten in der Datenbank:")
    for col in sorted(all_columns):
        count = sum(1 for case in cases if isinstance(case, dict) and col in case and case[col] not in [None, ""])
        print(f"      - {col}: {count} befüllte Einträge")
    
    print("\nModularer AFM Test abgeschlossen!")

if __name__ == "__main__":
    test_modular_afm_functionality()
