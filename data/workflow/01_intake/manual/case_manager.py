#!/usr/bin/env python3
"""
AFMTool - Interaktives Case Management
Ermöglicht das Erstellen, Bearbeiten und Archivieren von Cases.
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# Zum Importieren der AFM Utils
sys.path.append(str(Path(__file__).parent.parent.parent.parent.parent))
from utils.afm_utils import add_timestamp_to_case, update_case_afm_string
from utils.logger import log_action

class InteractiveCaseManager:
    def __init__(self):
        self.cases_file = Path(__file__).parent.parent.parent.parent.parent / "data" / "cases.json"
        
    def load_cases(self):
        """Lade alle Cases aus der Datenbank"""
        if self.cases_file.exists():
            with open(self.cases_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data.get("cases", [])
        return []
    
    def save_cases(self, cases):
        """Speichere Cases zurück in die Datenbank"""
        data = {"cases": cases}
        with open(self.cases_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def create_new_case(self):
        """1. Neuen Fall erstellen"""
        print("=== 📝 Neuen Fall erstellen ===")
        print()
        
        quelle = input("Quelle eingeben: ").strip()
        fundstellen = input("Fundstellen eingeben: ").strip()
        
        if not quelle or not fundstellen:
            print("❌ Quelle und Fundstellen sind erforderlich!")
            return
        
        # Neuen Case erstellen
        new_case = {
            "quelle": quelle,
            "fundstellen": fundstellen,
            "afm_string": "",
            "zeitstempel": []
        }
        
        # Erfassungs-Zeitstempel hinzufügen
        new_case = add_timestamp_to_case(new_case, "erfassung")
        
        # AFM String generieren
        new_case = update_case_afm_string(new_case)
        
        # Zur Datenbank hinzufügen
        cases = self.load_cases()
        cases.append(new_case)
        self.save_cases(cases)
        
        # Logging
        log_action("CREATE_CASE", f"Neuer Fall: {quelle[:30]}...")
        
        print("\\n✅ Fall erfolgreich erstellt!")
        print(f"Quelle: {new_case['quelle']}")
        print(f"Fundstellen: {new_case['fundstellen']}")
        print(f"AFM String: {new_case['afm_string'][:80]}...")
        print(f"Zeitstempel: {len(new_case['zeitstempel'])}")
        print(f"Gesamt Cases: {len(cases)}")
    
    def edit_existing_case(self):
        """2. Bestehenden Fall bearbeiten"""
        print("=== ✏️ Bestehenden Fall bearbeiten ===")
        print()
        
        cases = self.load_cases()
        if not cases:
            print("❌ Keine Cases gefunden!")
            return
        
        # Cases anzeigen
        print("Verfügbare Cases:")
        for i, case in enumerate(cases, 1):
            status = "🔄 Offen" if len(case["zeitstempel"]) < 4 else "✅ Archiviert"
            print(f"  {i:2d}. {status} | {case['quelle'][:40]:<40} | {len(case['zeitstempel'])}/4 Zeitstempel")
        print()
        
        # Case auswählen
        try:
            choice = int(input(f"Case auswählen (1-{len(cases)}): ")) - 1
            if choice < 0 or choice >= len(cases):
                print("❌ Ungültige Auswahl!")
                return
        except ValueError:
            print("❌ Bitte Zahl eingeben!")
            return
        
        selected_case = cases[choice]
        print(f"\\n📋 Case {choice+1} ausgewählt:")
        print(f"Quelle: {selected_case['quelle']}")
        print(f"Fundstellen: {selected_case['fundstellen']}")
        print(f"Zeitstempel: {len(selected_case['zeitstempel'])}/4")
        print()
        
        # Bearbeitungsoptionen
        print("Bearbeitungsoptionen:")
        print("  1. Quelle ändern")
        print("  2. Fundstellen ändern")
        print("  3. Zeitstempel hinzufügen")
        print("  4. Case-Details anzeigen")
        print()
        
        action = input("Aktion wählen (1-4): ").strip()
        
        if action == "1":
            neue_quelle = input(f"Neue Quelle (aktuell: {selected_case['quelle']}): ").strip()
            if neue_quelle:
                old_quelle = selected_case['quelle']
                selected_case['quelle'] = neue_quelle
                # AFM String neu generieren
                selected_case = update_case_afm_string(selected_case)
                log_action("EDIT_CASE", f"Quelle geändert: {old_quelle[:20]}... → {neue_quelle[:20]}...")
                print("✅ Quelle aktualisiert und AFM String neu generiert!")
        
        elif action == "2":
            neue_fundstellen = input(f"Neue Fundstellen (aktuell: {selected_case['fundstellen']}): ").strip()
            if neue_fundstellen:
                old_fundstellen = selected_case['fundstellen']
                selected_case['fundstellen'] = neue_fundstellen
                # AFM String neu generieren
                selected_case = update_case_afm_string(selected_case)
                log_action("EDIT_CASE", f"Fundstellen geändert: {old_fundstellen[:20]}... → {neue_fundstellen[:20]}...")
                print("✅ Fundstellen aktualisiert und AFM String neu generiert!")
        
        elif action == "3":
            # Verfügbare Zeitstempel-Typen
            existing_types = [ts.split(':')[0] for ts in selected_case['zeitstempel']]
            available_types = [t for t in ["erfassung", "verarbeitung", "validierung", "archivierung"] 
                             if t not in existing_types]
            
            if not available_types:
                print("❌ Alle Zeitstempel-Typen bereits vorhanden!")
            else:
                print("Verfügbare Zeitstempel-Typen:")
                for i, ts_type in enumerate(available_types, 1):
                    print(f"  {i}. {ts_type}")
                
                try:
                    ts_choice = int(input(f"Zeitstempel-Typ wählen (1-{len(available_types)}): ")) - 1
                    if 0 <= ts_choice < len(available_types):
                        ts_type = available_types[ts_choice]
                        selected_case = add_timestamp_to_case(selected_case, ts_type)
                        # AFM String neu generieren
                        selected_case = update_case_afm_string(selected_case)
                        log_action("ADD_TIMESTAMP", f"Zeitstempel '{ts_type}' zu Case hinzugefügt")
                        print(f"✅ Zeitstempel '{ts_type}' hinzugefügt!")
                    else:
                        print("❌ Ungültige Auswahl!")
                except ValueError:
                    print("❌ Bitte Zahl eingeben!")
        
        elif action == "4":
            print("\\n📊 Case-Details:")
            print(f"Quelle: {selected_case['quelle']}")
            print(f"Fundstellen: {selected_case['fundstellen']}")
            print(f"AFM String: {selected_case['afm_string']}")
            print("Zeitstempel:")
            for i, ts in enumerate(selected_case['zeitstempel'], 1):
                print(f"  {i}. {ts}")
            return  # Keine Änderungen
        
        else:
            print("❌ Ungültige Aktion!")
            return
        
        # Änderungen speichern
        cases[choice] = selected_case
        self.save_cases(cases)
        print("\\n💾 Änderungen gespeichert!")
    
    def archive_case(self):
        """3. Fall archivieren (alle 4 Zeitstempel setzen)"""
        print("=== 📁 Fall archivieren ===")
        print()
        
        cases = self.load_cases()
        if not cases:
            print("❌ Keine Cases gefunden!")
            return
        
        # Nur offene Cases anzeigen (< 4 Zeitstempel)
        open_cases = [(i, case) for i, case in enumerate(cases) if len(case["zeitstempel"]) < 4]
        
        if not open_cases:
            print("❌ Keine offenen Cases zum Archivieren gefunden!")
            return
        
        print("Offene Cases (zum Archivieren):")
        for display_idx, (real_idx, case) in enumerate(open_cases, 1):
            missing = 4 - len(case["zeitstempel"])
            print(f"  {display_idx:2d}. {case['quelle'][:50]:<50} | {len(case['zeitstempel'])}/4 Zeitstempel (fehlen: {missing})")
        print()
        
        # Case auswählen
        try:
            choice = int(input(f"Case auswählen (1-{len(open_cases)}): ")) - 1
            if choice < 0 or choice >= len(open_cases):
                print("❌ Ungültige Auswahl!")
                return
        except ValueError:
            print("❌ Bitte Zahl eingeben!")
            return
        
        real_idx, selected_case = open_cases[choice]
        
        print(f"\\n📋 Case zur Archivierung:")
        print(f"Quelle: {selected_case['quelle']}")
        print(f"Fundstellen: {selected_case['fundstellen']}")
        print(f"Aktuelle Zeitstempel: {len(selected_case['zeitstempel'])}/4")
        print()
        
        # Fehlende Zeitstempel hinzufügen
        existing_types = [ts.split(':')[0] for ts in selected_case['zeitstempel']]
        all_types = ["erfassung", "verarbeitung", "validierung", "archivierung"]
        missing_types = [t for t in all_types if t not in existing_types]
        
        if missing_types:
            print(f"Fehlende Zeitstempel werden hinzugefügt: {', '.join(missing_types)}")
            for ts_type in missing_types:
                selected_case = add_timestamp_to_case(selected_case, ts_type)
                print(f"  ✅ {ts_type}")
        
        # AFM String neu generieren
        selected_case = update_case_afm_string(selected_case)
        
        # Speichern
        cases[real_idx] = selected_case
        self.save_cases(cases)
        
        # Logging
        log_action("ARCHIVE_CASE", f"Case archiviert: {selected_case['quelle'][:30]}... (4/4 Zeitstempel)")
        
        print("\\n🎉 Case erfolgreich archiviert!")
        print(f"Alle 4 Zeitstempel gesetzt: {len(selected_case['zeitstempel'])}/4")
        print("AFM String aktualisiert.")
    
    def show_statistics(self):
        """Zeige Statistiken über alle Cases"""
        cases = self.load_cases()
        if not cases:
            print("❌ Keine Cases gefunden!")
            return
        
        open_cases = [c for c in cases if len(c["zeitstempel"]) < 4]
        archived_cases = [c for c in cases if len(c["zeitstempel"]) == 4]
        
        print("\\n📊 Case-Statistiken:")
        print(f"Gesamt Cases: {len(cases)}")
        print(f"Offene Cases: {len(open_cases)} (🔄)")
        print(f"Archivierte Cases: {len(archived_cases)} (✅)")
        print()
    
    def main_menu(self):
        """Hauptmenü"""
        while True:
            print("\\n" + "="*60)
            print("🔧 AFMTool - Interaktives Case Management")
            print("="*60)
            
            self.show_statistics()
            
            print("Optionen:")
            print("  1. 📝 Neuen Fall erstellen")
            print("  2. ✏️  Bestehenden Fall bearbeiten")
            print("  3. 📁 Fall archivieren")
            print("  4. 📊 Alle Cases anzeigen")
            print("  0. ❌ Beenden")
            print()
            
            choice = input("Wählen Sie eine Option (0-4): ").strip()
            
            if choice == "1":
                self.create_new_case()
            elif choice == "2":
                self.edit_existing_case()
            elif choice == "3":
                self.archive_case()
            elif choice == "4":
                self.show_all_cases()
            elif choice == "0":
                print("\\n👋 Auf Wiedersehen!")
                log_action("SYSTEM_STOP", "Interaktives Case Management beendet")
                break
            else:
                print("❌ Ungültige Option!")
            
            input("\\n⏸️  Drücken Sie Enter für das Hauptmenü...")
    
    def show_all_cases(self):
        """Zeige alle Cases in übersichtlicher Form"""
        cases = self.load_cases()
        if not cases:
            print("❌ Keine Cases gefunden!")
            return
        
        print("\\n📋 Alle Cases:")
        print("-" * 100)
        print(f"{'Nr':<3} {'Status':<12} {'Quelle':<35} {'Fundstellen':<35} {'Zeitstempel':<10}")
        print("-" * 100)
        
        for i, case in enumerate(cases, 1):
            status = "✅ Archiviert" if len(case["zeitstempel"]) == 4 else f"🔄 Offen ({len(case['zeitstempel'])}/4)"
            quelle = case['quelle'][:34] + "..." if len(case['quelle']) > 34 else case['quelle']
            fundstellen = case['fundstellen'][:34] + "..." if len(case['fundstellen']) > 34 else case['fundstellen']
            
            print(f"{i:<3} {status:<12} {quelle:<35} {fundstellen:<35} {len(case['zeitstempel'])}/4")

def main():
    """Hauptprogramm"""
    manager = InteractiveCaseManager()
    log_action("SYSTEM_START", "Interaktives Case Management gestartet")
    manager.main_menu()

if __name__ == "__main__":
    main()
