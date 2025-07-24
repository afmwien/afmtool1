"""
Script zum Hinzufügen von Hash-UUIDs zu cases.json
"""
import json
import hashlib
from pathlib import Path

def generate_hash_uuid(case):
    """5-stelligen Hash aus erfassung-Zeitstempel generieren"""
    for ts in case.get("zeitstempel", []):
        if ts.startswith("erfassung:"):
            timestamp_part = ts.replace("erfassung:", "")
            hash_obj = hashlib.md5(timestamp_part.encode('utf-8'))
            short_hash = hash_obj.hexdigest()[:5].upper()
            return short_hash
    return "ERROR"

def add_uuids_to_cases():
    """Fügt Hash-UUIDs zu allen Cases hinzu"""
    
    # JSON laden
    json_path = Path(__file__).parent / "data" / "cases.json"
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # UUID zu jedem Case hinzufügen
    updated_count = 0
    for case in data.get('cases', []):
        if 'uuid' not in case:
            case['uuid'] = generate_hash_uuid(case)
            updated_count += 1
    
    # Backup erstellen
    backup_path = json_path.parent / "cases_backup_before_uuid.json"
    with open(backup_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    # Aktualisierte JSON speichern
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ {updated_count} Cases mit UUIDs erweitert")
    print(f"💾 Backup gespeichert: {backup_path}")
    
    # Übersicht der UUIDs anzeigen
    print(f"\n📋 UUID-Übersicht:")
    for i, case in enumerate(data.get('cases', [])[:5]):
        fallnummer = case.get('fallnummer', 'KEINE')
        uuid = case.get('uuid', 'FEHLT')
        quelle_short = case.get('quelle', '')[:50] + "..." if len(case.get('quelle', '')) > 50 else case.get('quelle', '')
        print(f"  {i+1}. {uuid}: {fallnummer} | {quelle_short}")

if __name__ == "__main__":
    add_uuids_to_cases()
