"""
Data Service Layer für AFMTool1 - Pure AFM Implementation
"""
import json
import os
from pathlib import Path
from datetime import datetime
import sys

# Utils importieren
sys.path.append(str(Path(__file__).parent.parent.parent))
from utils.afm_pure import AFMPureStorage
from .export_service import AFMExportService

class DataService:
    """Service Layer für Pure AFM-String Operationen"""
    
    def __init__(self, cases_file):
        self.cases_file = cases_file
        self.pure_storage = AFMPureStorage(cases_file)
        self.exports_dir = Path(cases_file).parent / "exports"
        self.exports_dir.mkdir(exist_ok=True)
        self.export_service = AFMExportService(cases_file, self.exports_dir)
        
        print(f"📂 [PURE AFM] Storage: {self.pure_storage.storage_file}")
        self._initialize_pure_data()
    
    def _initialize_pure_data(self):
        """Lädt Pure AFM-Daten"""
        try:
            print("🔄 [PURE AFM] Initialisiere Pure AFM System...")
            cases = self.pure_storage.load_pure_afm_data()
            print(f"✅ [PURE AFM] {len(cases)} Cases aus AFM-Strings geladen")
        except Exception as e:
            print(f"⚠️ [PURE AFM] Initialisierung: {e}")
    
    def get_cases(self):
        """Cases aus Pure AFM-Strings laden"""
        return self.pure_storage.load_pure_afm_data()
    
    def _save_cases(self, data):
        """Cases in Pure AFM Format speichern"""
        try:
            cases = data.get("cases", [])
            self.pure_storage.save_pure_afm_data(cases)
            print(f"💾 [PURE AFM] {len(cases)} Cases als AFM-Strings gespeichert")
        except Exception as e:
            print(f"❌ [PURE AFM] Speichern fehlgeschlagen: {e}")
    
    def get_case_status(self, case):
        """Status eines Cases ermitteln anhand der Zeitstempel"""
        timestamps = case.get("zeitstempel", [])
        if not timestamps:
            return "neu"
        
        if any("archivierung:" in ts for ts in timestamps):
            return "archivierung"
        elif any("validierung:" in ts for ts in timestamps):
            return "validierung"
        elif any("verarbeitung:" in ts for ts in timestamps):
            return "verarbeitung"
        else:
            return "erfassung"
    
    def update_case(self, case_index, updates):
        """Case aktualisieren und als AFM-String speichern"""
        cases = self.get_cases()
        if case_index >= len(cases):
            return False
            
        case = cases[case_index]
        for key, value in updates.items():
            case[key] = value
        
        self._save_cases({"cases": cases})
        return True
    
    def regenerate_afm_string(self, case_index):
        """AFM-String neu generieren (Pure AFM: automatisch)"""
        return True
    
    def delete_case(self, case_index):
        """Case löschen"""
        cases = self.get_cases()
        if case_index >= len(cases):
            return False, None
            
        deleted_case = cases.pop(case_index)
        self._save_cases({"cases": cases})
        return True, deleted_case
    
    def create_case(self, quelle, fundstellen):
        """Neuen Case erstellen"""
        new_case = {
            "quelle": quelle,
            "fundstellen": fundstellen,
            "zeitstempel": [f"erfassung:{datetime.now().strftime('%Y-%m-%dT%H')}"]
        }
        
        cases = self.get_cases()
        cases.append(new_case)
        self._save_cases({"cases": cases})
        return new_case
    
    def create_empty_case(self):
        """Leeren Case erstellen"""
        new_case = {
            "quelle": "",
            "fundstellen": "",
            "zeitstempel": [f"erfassung:{datetime.now().strftime('%Y-%m-%dT%H')}"]
        }
        
        cases = self.get_cases()
        cases.append(new_case)
        self._save_cases({"cases": cases})
        return len(cases) - 1
    
    def cleanup_empty_cases(self):
        """Leere Cases entfernen"""
        cases = self.get_cases()
        cleaned_cases = [
            case for case in cases 
            if case.get('quelle', '').strip() or case.get('fundstellen', '').strip()
        ]
        
        if len(cleaned_cases) != len(cases):
            self._save_cases({"cases": cleaned_cases})
    
    def export_to_json(self):
        """Export erstellen"""
        return self.export_service.create_export()
    
    def import_from_json(self, file_path):
        """Import aus Datei"""
        cases = self.export_service.load_export_cases(Path(file_path))
        if cases:
            self._save_cases({"cases": cases})
        return len(cases)
    
    def sync_session_data(self):
        """Session-Daten synchronisieren (Pure AFM: direkt persistent)"""
        cases = self.get_cases()
        print(f"🔄 [SYNC] Pure AFM System: {len(cases)} Cases synchronisiert")
        return True
    
    def sync_and_shutdown(self):
        """Synchronisieren und herunterfahren"""
        return self.sync_session_data()
