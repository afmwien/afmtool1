"""
AFMTool1 - Modulare AFM String Utilities
Vollständig modulare AFM String-Funktionen für dynamische Spalten mit Zeitstempel-Unterstützung
"""

import json
import datetime
from pathlib import Path

def generate_afm_string_for_case(case_data, exclude_fields=None):
    """
    Generiert AFM String für einen Case mit ALLEN befüllten Spalten
    Vollständig modular - arbeitet mit beliebigen Spalten
    
    Args:
        case_data (dict): Case-Daten
        exclude_fields (list): Felder die nicht im AFM String enthalten sein sollen
        
    Returns:
        str: JSON-kodierter AFM String
    """
    if exclude_fields is None:
        exclude_fields = ['afm_string']  # AFM String selbst ausschließen
    
    # Nur befüllte Felder sammeln (nicht None, nicht leer)
    afm_data = {}
    for key, value in case_data.items():
        if key not in exclude_fields and value is not None and value != "":
            afm_data[key] = value
    
    # Als JSON-String kodieren
    return json.dumps(afm_data, ensure_ascii=False, sort_keys=True)

def add_timestamp_to_case(case_data, timestamp_type="erfassung"):
    """
    Fügt einen Zeitstempel zum Case hinzu
    
    Args:
        case_data (dict): Case-Daten
        timestamp_type (str): Art des Zeitstempels (erfassung, verarbeitung, validierung, archivierung)
        
    Returns:
        dict: Aktualisierte Case-Daten mit neuem Zeitstempel
    """
    if "zeitstempel" not in case_data:
        case_data["zeitstempel"] = []
    
    # Aktueller Zeitstempel im ISO-Format
    current_timestamp = datetime.datetime.now().isoformat()
    
    # Zeitstempel mit Typ-Info hinzufügen
    timestamp_entry = f"{timestamp_type}:{current_timestamp}"
    case_data["zeitstempel"].append(timestamp_entry)
    
    return case_data

def get_timestamps_from_case(case_data):
    """
    Extrahiert alle Zeitstempel aus einem Case
    
    Args:
        case_data (dict): Case-Daten
        
    Returns:
        list: Liste von Zeitstempel-Dictionaries mit Typ und Zeit
    """
    if "zeitstempel" not in case_data:
        return []
    
    timestamps = []
    for timestamp_entry in case_data["zeitstempel"]:
        if ":" in timestamp_entry:
            timestamp_type, timestamp_value = timestamp_entry.split(":", 1)
            timestamps.append({
                "type": timestamp_type,
                "timestamp": timestamp_value
            })
        else:
            # Fallback für einfache Zeitstempel
            timestamps.append({
                "type": "unknown",
                "timestamp": timestamp_entry
            })
    
    return timestamps

def update_case_afm_string(case_data):
    """
    Aktualisiert den AFM String für einen Case mit ALLEN befüllten Spalten
    
    Args:
        case_data (dict): Case-Daten (wird modifiziert)
        
    Returns:
        dict: Aktualisierter Case mit AFM String
    """
    # AFM String generieren (ohne den afm_string selbst)
    afm_string = generate_afm_string_for_case(case_data, exclude_fields=['afm_string'])
    
    # AFM String hinzufügen/aktualisieren
    case_data['afm_string'] = afm_string
    
    return case_data

def update_all_afm_strings_in_database(database_path="data/cases.json"):
    """
    Aktualisiert AFM Strings für ALLE Cases in der Datenbank
    Vollständig modular - erkennt automatisch alle Spalten
    
    Args:
        database_path (str): Pfad zur Datenbank
        
    Returns:
        tuple: (success: bool, updated_count: int, message: str)
    """
    try:
        # Datenbank laden
        with open(database_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        cases = data.get('cases', [])
        if not cases:
            return False, 0, "Keine Cases gefunden"
        
        updated_count = 0
        
        # Jeden Case aktualisieren
        for i, case in enumerate(cases):
            if isinstance(case, dict):
                # Alle befüllten Spalten für AFM String sammeln
                original_afm = case.get('afm_string', '')
                updated_case = update_case_afm_string(case)
                
                # Prüfen ob sich etwas geändert hat
                if updated_case['afm_string'] != original_afm:
                    updated_count += 1
                
                cases[i] = updated_case
        
        # Datenbank speichern
        with open(database_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return True, updated_count, f"AFM Strings für {updated_count} Cases aktualisiert"
        
    except Exception as e:
        return False, 0, f"Fehler: {str(e)}"

def validate_afm_strings(database_path="data/cases.json"):
    """
    Validiert alle AFM Strings in der Datenbank
    Prüft ob sie alle befüllten Spalten enthalten
    
    Returns:
        list: Liste mit Validierungsergebnissen
    """
    try:
        with open(database_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        cases = data.get('cases', [])
        validation_results = []
        
        for i, case in enumerate(cases):
            if isinstance(case, dict):
                result = {
                    "case_index": i,
                    "quelle": case.get('quelle', 'Unbekannt'),
                    "has_afm_string": 'afm_string' in case,
                    "afm_valid": False,
                    "missing_fields": [],
                    "afm_fields": [],
                    "all_fields": list(case.keys())
                }
                
                # AFM String analysieren
                afm_string = case.get('afm_string', '')
                if afm_string:
                    try:
                        afm_data = json.loads(afm_string)
                        result["afm_fields"] = list(afm_data.keys())
                        
                        # Prüfen welche Felder fehlen (außer afm_string selbst)
                        case_fields = set(case.keys()) - {'afm_string'}
                        afm_fields = set(afm_data.keys())
                        
                        # Nur befüllte Felder prüfen
                        filled_case_fields = {k for k, v in case.items() 
                                            if k != 'afm_string' and v is not None and v != ""}
                        
                        missing = filled_case_fields - afm_fields
                        result["missing_fields"] = list(missing)
                        result["afm_valid"] = len(missing) == 0
                        
                    except json.JSONDecodeError:
                        result["afm_valid"] = False
                        result["missing_fields"] = ["INVALID_JSON"]
                
                validation_results.append(result)
        
        return validation_results
        
    except Exception as e:
        return [{"error": str(e)}]

def add_new_case_with_afm(case_data, database_path="data/cases.json"):
    """
    Fügt einen neuen Case mit automatischem AFM String hinzu
    Vollständig modular für beliebige Spalten
    
    Args:
        case_data (dict): Case-Daten (beliebige Spalten)
        database_path (str): Pfad zur Datenbank
        
    Returns:
        tuple: (success: bool, case: dict, message: str)
    """
    try:
        # Datenbank laden
        with open(database_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # AFM String generieren
        case_with_afm = update_case_afm_string(case_data.copy())
        
        # Case hinzufügen
        data["cases"].append(case_with_afm)
        
        # Speichern
        with open(database_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return True, case_with_afm, "Case erfolgreich hinzugefügt"
        
    except Exception as e:
        return False, {}, f"Fehler beim Hinzufügen: {str(e)}"

def main():
    """Test der modularen AFM String-Funktionen"""
    print("=== AFMTool1 - Modulare AFM String Utilities ===")
    
    # 1. Validierung der aktuellen AFM Strings
    print("\n1. Validiere aktuelle AFM Strings...")
    validation_results = validate_afm_strings()
    
    for result in validation_results:
        if "error" in result:
            print(f"   ❌ Fehler: {result['error']}")
        else:
            status = "✅" if result["afm_valid"] else "⚠️"
            quelle = result["quelle"]
            print(f"   {status} Case {result['case_index']+1} ({quelle}):")
            print(f"       Alle Felder: {result['all_fields']}")
            print(f"       AFM Felder: {result['afm_fields']}")
            if result["missing_fields"]:
                print(f"       ⚠️  Fehlende Felder: {result['missing_fields']}")
    
    # 2. AFM Strings aktualisieren
    print("\n2. Aktualisiere alle AFM Strings...")
    success, count, message = update_all_afm_strings_in_database()
    print(f"   {message}")
    
    # 3. Test: Neuen Case mit zusätzlichen Spalten hinzufügen
    print("\n3. Test: Neuer Case mit zusätzlichen Spalten...")
    test_case = {
        "quelle": "Markenschutzregister Wien",
        "fundstellen": "AT 123456, eingetragen 23.07.2025",
        "kategorie": "Markenrecht",
        "status": "aktiv",
        "bemerkung": "Test für modulare AFM Strings"
    }
    
    success, new_case, message = add_new_case_with_afm(test_case)
    if success:
        print(f"   ✅ {message}")
        print(f"   AFM String: {new_case.get('afm_string', 'Nicht gefunden')}")
    else:
        print(f"   ❌ {message}")
    
    # 4. Finale Validierung
    print("\n4. Finale Validierung...")
    final_validation = validate_afm_strings()
    valid_count = sum(1 for r in final_validation if r.get("afm_valid", False))
    total_count = len(final_validation)
    print(f"   ✅ {valid_count}/{total_count} Cases haben gültige AFM Strings")
    
    print("\nModulare AFM String Utilities abgeschlossen!")

if __name__ == "__main__":
    main()
