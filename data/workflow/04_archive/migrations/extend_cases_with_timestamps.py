#!/usr/bin/env python3
"""
Erweitert die bestehende cases.json um Zeitstempel-Arrays

VERSCHOBEN VON: Hauptverzeichnis  
VERSCHOBEN NACH: data/workflow/04_archive/migrations/
GRUND: Historische Migration, gehört ins Archiv für Dokumentationszwecke
DATUM: 23.07.2025
"""

import json
import time
import datetime
import sys
from pathlib import Path

# Pfad zu utils anpassen
sys.path.append(str(Path(__file__).parent.parent.parent.parent.parent))
from utils.afm_utils import add_timestamp_to_case, update_case_afm_string

def extend_cases_with_timestamps():
    """Erweitert alle Cases in cases.json um Zeitstempel"""
    print("=== Erweitere cases.json um Zeitstempel ===\n")
    
    # Bestehende Datenbank laden
    cases_path = Path(__file__).parent.parent.parent.parent.parent / "data" / "cases.json"
    with open(cases_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"1. Lade {len(data['cases'])} bestehende Cases")
    
    # Verschiedene Zeitstempel-Szenarien
    timestamp_scenarios = [
        ["erfassung", "verarbeitung", "validierung", "archivierung"],  # Vollständig
        ["erfassung", "verarbeitung", "validierung"],                   # Fast vollständig
        ["erfassung", "verarbeitung"],                                   # In Bearbeitung
        ["erfassung", "verarbeitung", "validierung", "archivierung"],  # Vollständig
        ["erfassung", "verarbeitung"],                                   # In Bearbeitung
        ["erfassung", "verarbeitung", "validierung", "archivierung"],  # Vollständig
    ]
    
    # Jeden Case erweitern
    for i, case in enumerate(data['cases']):
        scenario = timestamp_scenarios[i % len(timestamp_scenarios)]
        
        print(f"2.{i+1} Case {i+1}: {case['quelle']}")
        print(f"     Zeitstempel-Szenario: {', '.join(scenario)}")
        
        # Zeitstempel hinzufügen
        for j, ts_type in enumerate(scenario):
            # Simuliere zeitliche Abfolge
            base_time = datetime.datetime.now() - datetime.timedelta(hours=len(scenario)-j)
            case['zeitstempel'] = case.get('zeitstempel', [])
            timestamp_entry = f"{ts_type}:{base_time.isoformat()}"
            case['zeitstempel'].append(timestamp_entry)
        
        # AFM String aktualisieren
        case = update_case_afm_string(case)
        
        print(f"     ✓ {len(case['zeitstempel'])} Zeitstempel hinzugefügt")
    
    # Erweiterte Datenbank speichern
    with open(cases_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ cases.json erfolgreich erweitert!")
    print(f"   - Alle {len(data['cases'])} Cases haben jetzt Zeitstempel")
    print(f"   - AFM Strings automatisch aktualisiert")
    print(f"   - Nur 1 neue Spalte hinzugefügt: 'zeitstempel'")
    
    return data

def show_extended_structure():
    """Zeigt die erweiterte Struktur der Datenbank"""
    print("\n=== Erweiterte Datenbank-Struktur ===\n")
    
    cases_path = Path(__file__).parent.parent.parent.parent.parent / "data" / "cases.json"
    with open(cases_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Alle verfügbaren Spalten sammeln
    all_columns = set()
    for case in data['cases']:
        all_columns.update(case.keys())
    
    print(f"Spalten insgesamt: {len(all_columns)}")
    for col in sorted(all_columns):
        print(f"  - {col}")
    
    # Beispiel-Case zeigen
    if data['cases']:
        print(f"\nBeispiel-Case (Case 1):")
        print(json.dumps(data['cases'][0], ensure_ascii=False, indent=2))
    
    print(f"\n📊 Statistiken:")
    for i, case in enumerate(data['cases'], 1):
        ts_count = len(case.get('zeitstempel', []))
        afm_length = len(case.get('afm_string', ''))
        print(f"  Case {i}: {ts_count} Zeitstempel, AFM String: {afm_length} Zeichen")

if __name__ == "__main__":
    print("⚠️  HINWEIS: Dies ist eine archivierte Migrationsdatei.")
    print("⚠️  Sie sollte normalerweise nicht direkt ausgeführt werden.")
    print("⚠️  Verwenden Sie diese nur für Dokumentation oder Wiederherstellung.\n")
    
    # Datenbank erweitern
    extended_data = extend_cases_with_timestamps()
    
    # Struktur anzeigen
    show_extended_structure()
