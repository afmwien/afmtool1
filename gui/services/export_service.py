#!/usr/bin/env python3
"""
AFM Pure Export Service  
Direkter AFM-String Export ohne Case-Rekonstruktion
"""

import json
from datetime import datetime
from pathlib import Path
import sys

# Utils importieren
sys.path.append(str(Path(__file__).parent.parent))
from utils.logger import log_action
from utils.afm_pure import AFMPureStorage

class AFMExportService:
    """Service für direkten AFM-String Export"""
    
    def __init__(self, cases_file, exports_dir):
        self.pure_storage = AFMPureStorage(cases_file)
        self.exports_dir = Path(exports_dir)
        self.exports_dir.mkdir(exist_ok=True)
    
    def create_export(self):
        """Erstellt direkten AFM-String Export"""
        try:
            print("📤 [PURE EXPORT] Starte direkten AFM-Export...")
            
            # Pure AFM-Daten laden
            cases = self.pure_storage.load_pure_afm_data()
            if not cases:
                print("⚠️ [PURE EXPORT] Keine AFM-Daten gefunden")
                return False, "Keine AFM-Daten gefunden"
            
            print(f"📂 [LOAD] {len(cases)} Cases aus Pure AFM geladen")
            
            # Direkte AFM-Strings aus Storage extrahieren
            with open(self.pure_storage.storage_file, 'r', encoding='utf-8') as f:
                pure_data = json.load(f)
            
            afm_strings = pure_data.get('afm_strings', [])
            
            # Export-Datei erstellen
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            export_file = self.exports_dir / f"afm_pure_export_{timestamp}.json"
            
            export_data = {
                "export_timestamp": datetime.now().isoformat(),
                "export_version": "pure_v1.0",
                "case_count": len(afm_strings),
                "format": "encrypted_afm_strings",
                "afm_strings": afm_strings
            }
            
            # Export speichern
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            print(f"💾 [SAVE] Pure Export erstellt: {export_file.name}")
            
            # Alte Exports bereinigen
            self._cleanup_old_exports()
            
            log_action(f"Pure AFM Export: {export_file.name} ({len(afm_strings)} AFM-Strings)")
            print(f"✅ [PURE EXPORT] Direkter AFM-Export abgeschlossen")
            return True, export_file
            
        except Exception as e:
            return False, f"Pure Export-Fehler: {str(e)}"
    
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
        """Lädt Cases aus Pure AFM Export"""
        try:
            if export_file is None:
                export_file = self.get_latest_export()
                print("📥 [PURE IMPORT] Lade neuesten Pure Export...")
            else:
                print(f"📥 [PURE IMPORT] Lade Export: {export_file.name}")
            
            if not export_file or not export_file.exists():
                print("❌ [PURE IMPORT] Export-Datei nicht gefunden")
                return []
            
            with open(export_file, 'r', encoding='utf-8') as f:
                export_data = json.load(f)
            
            afm_strings = export_data.get("afm_strings", [])
            print(f"📂 [LOAD] {len(afm_strings)} Verschlüsselte AFM-Strings geladen")
            
            # AFM-Strings direkt zu Cases konvertieren
            cases = []
            for i, encrypted_afm in enumerate(afm_strings):
                try:
                    case_data = self.pure_storage._decrypt_afm_string(encrypted_afm)
                    if case_data:
                        case = json.loads(case_data)
                        cases.append(case)
                except Exception:
                    print(f"⚠️ [PARSE] AFM-String {i+1} ungültig - übersprungen")
                    continue
            
            print(f"✅ [PURE IMPORT] {len(cases)} Cases erfolgreich dekodiert")
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
