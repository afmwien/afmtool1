#!/usr/bin/env python3
"""
AFM Export Service
Exportiert AFM-Strings aus cases.json in versionierte Export-Dateien
"""

import json
from datetime import datetime
from pathlib import Path
import sys

# Utils importieren
sys.path.append(str(Path(__file__).parent.parent))
from utils.logger import log_action

class AFMExportService:
    """Service für AFM-String Export mit Versionierung"""
    
    def __init__(self, cases_file, exports_dir):
        self.cases_file = Path(cases_file)
        self.exports_dir = Path(exports_dir)
        self.exports_dir.mkdir(exist_ok=True)
    
    def create_export(self):
        """Erstellt neuen AFM-String Export"""
        try:
            print("📤 [EXPORT] Starte AFM-Export aus cases.json...")
            
            # Cases laden
            with open(self.cases_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            cases = data.get("cases", [])
            if not cases:
                print("⚠️ [EXPORT] Keine Cases zum Exportieren gefunden")
                return False, "Keine Cases zum Exportieren gefunden"
            
            print(f"📂 [LOAD] {len(cases)} Cases aus cases.json geladen")
            
            # AFM-Strings extrahieren
            afm_strings = []
            for case in cases:
                afm_string = case.get("afm_string")
                if afm_string:
                    afm_strings.append(afm_string)
            
            if not afm_strings:
                print("⚠️ [EXPORT] Keine AFM-Strings gefunden")
                return False, "Keine AFM-Strings gefunden"
            
            print(f"📝 [EXTRACT] {len(afm_strings)} AFM-Strings extrahiert")
            
            # Export-Datei erstellen
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            export_file = self.exports_dir / f"afm_export_{timestamp}.json"
            
            export_data = {
                "export_timestamp": datetime.now().isoformat(),
                "export_version": "1.0",
                "case_count": len(afm_strings),
                "afm_strings": afm_strings
            }
            
            # Export speichern
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            print(f"💾 [SAVE] Export-Datei erstellt: {export_file.name}")
            
            # Alte Exports bereinigen (nur letzte 10 behalten)
            self._cleanup_old_exports()
            
            log_action(f"AFM Export erstellt: {export_file.name} ({len(afm_strings)} Cases)")
            print(f"✅ [EXPORT] AFM-Export erfolgreich abgeschlossen")
            return True, export_file
            
        except Exception as e:
            return False, f"Export-Fehler: {str(e)}"
    
    def get_latest_export(self):
        """Findet den neuesten Export"""
        try:
            export_files = list(self.exports_dir.glob("afm_export_*.json"))
            if not export_files:
                return None
            
            # Nach Datum sortieren (neuester zuerst)
            export_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            return export_files[0]
            
        except Exception:
            return None
    
    def load_export_cases(self, export_file=None):
        """Lädt Cases aus Export-Datei"""
        try:
            if export_file is None:
                export_file = self.get_latest_export()
                print("📥 [IMPORT] Lade neuesten Export...")
            else:
                print(f"📥 [IMPORT] Lade spezifischen Export: {export_file.name}")
            
            if not export_file or not export_file.exists():
                print("❌ [IMPORT] Export-Datei nicht gefunden")
                return []
            
            with open(export_file, 'r', encoding='utf-8') as f:
                export_data = json.load(f)
            
            afm_strings = export_data.get("afm_strings", [])
            print(f"📂 [LOAD] {len(afm_strings)} AFM-Strings aus Export geladen")
            
            cases = []
            
            # AFM-Strings zu Cases konvertieren
            for i, afm_string in enumerate(afm_strings):
                try:
                    case_data = json.loads(afm_string)
                    cases.append(case_data)
                except json.JSONDecodeError:
                    print(f"⚠️ [PARSE] AFM-String {i+1} ungültig - übersprungen")
                    continue
            
            print(f"✅ [IMPORT] {len(cases)} Cases erfolgreich konvertiert")
            return cases
            
        except Exception:
            return []
    
    def _cleanup_old_exports(self, keep_count=10):
        """Bereinigt alte Export-Dateien"""
        try:
            export_files = list(self.exports_dir.glob("afm_export_*.json"))
            if len(export_files) <= keep_count:
                return
            
            # Nach Datum sortieren (älteste zuerst)
            export_files.sort(key=lambda x: x.stat().st_mtime)
            
            # Alte Dateien löschen
            for old_file in export_files[:-keep_count]:
                old_file.unlink()
                
        except Exception:
            pass
