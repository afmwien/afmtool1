#!/usr/bin/env python3
"""
AFMTool Manual Entry System
Ermöglicht die direkte manuelle Eingabe von Fällen ohne Templates.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Zum Importieren der AFM Utils
sys.path.append(str(Path(__file__).parent.parent.parent.parent.parent))
from utils.afm_utils import add_timestamp_to_case, update_case_afm_string

class ManualEntrySystem:
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.cases_file = Path(__file__).parent.parent.parent.parent.parent / "data" / "cases.json"
        
    def create_new_case(self, quelle, fundstellen):
        """Erstelle einen neuen Fall direkt ohne Template."""
        # Erstelle neuen Fall
        new_case = {
            "quelle": quelle,
            "fundstellen": fundstellen,
            "afm_string": "",
            "zeitstempel": []
        }
        
        # Füge Erfassungs-Zeitstempel hinzu
        new_case = add_timestamp_to_case(new_case, "erfassung")
        
        # Generiere AFM String
        new_case = update_case_afm_string(new_case)
        
        return new_case
    
    def add_case_to_database(self, new_case):
        """Füge den Fall zur Hauptdatenbank hinzu."""
        # Lade existierende Fälle
        if self.cases_file.exists():
            with open(self.cases_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = {"cases": []}
        
        # Füge neuen Fall hinzu
        data["cases"].append(new_case)
        
        # Speichere zurück
        with open(self.cases_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Fall erfolgreich hinzugefügt! Gesamt: {len(data['cases'])} Fälle")
        return len(data["cases"])
    
    def interactive_entry(self):
        """Direkte interaktive Eingabe ohne Templates."""
        print("=== AFMTool Manual Entry System ===")
        print("Direkter Case-Input ohne Templates")
        print()
        
        # Eingabe der Daten
        print("Neuen Fall erstellen:")
        quelle = input("Quelle eingeben: ").strip()
        fundstellen = input("Fundstellen eingeben: ").strip()
        
        if not quelle or not fundstellen:
            print("❌ Quelle und Fundstellen sind erforderlich!")
            return
        
        # Erstelle Fall
        try:
            new_case = self.create_new_case(quelle, fundstellen)
            case_count = self.add_case_to_database(new_case)
            
            print("\n✅ Fall erfolgreich erstellt!")
            print(f"Quelle: {new_case['quelle']}")
            print(f"Fundstellen: {new_case['fundstellen']}")
            print(f"Zeitstempel: {len(new_case['zeitstempel'])}")
            print(f"AFM String: {new_case['afm_string'][:100]}...")
            print(f"Gesamt Cases in Datenbank: {case_count}")
            
        except Exception as e:
            print(f"❌ Fehler beim Erstellen des Falls: {e}")

def main():
    """Hauptfunktion für direkten Aufruf."""
    entry_system = ManualEntrySystem()
    entry_system.interactive_entry()

if __name__ == "__main__":
    main()
