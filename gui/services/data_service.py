"""
Data Service Layer für AFMTool1
Web-kompatible Datenoperationen
"""
import json
from pathlib import Path
from datetime import datetime
import sys

# Utils importieren
sys.path.append(str(Path(__file__).parent.parent.parent))
from utils.afm_utils import update_case_afm_string

class DataService:
    """Service Layer für Datenoperationen - Web-kompatibel"""
    
    def __init__(self, cases_file):
        self.cases_file = cases_file
    
    def get_cases(self):
        """Cases laden (API-ready)"""
        try:
            with open(self.cases_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("cases", [])
        except FileNotFoundError:
            return []
    
    def get_case_count(self):
        """Case-Anzahl ermitteln"""
        return len(self.get_cases())
    
    def get_case_status(self, case):
        """Aktuellen Status eines Cases ermitteln"""
        if not case.get("zeitstempel"):
            return "erfassung"  # Neu erstellte Cases sind NEU
        
        # Letzten Zeitstempel finden
        timestamps = case["zeitstempel"]
        if any("archivierung:" in ts for ts in timestamps):
            return "archivierung"
        elif any("validierung:" in ts for ts in timestamps):
            return "validierung"
        elif any("verarbeitung:" in ts for ts in timestamps):
            return "verarbeitung"
        else:
            return "erfassung"
    
    def advance_case_status(self, case_index):
        """Case zum nächsten Status weiterschalten"""
        cases = self.get_cases()
        if case_index >= len(cases):
            return False
            
        case = cases[case_index]
        current_status = self.get_case_status(case)
        
        # Status-Mapping für nächsten Schritt
        next_status_map = {
            "erfassung": "verarbeitung",
            "verarbeitung": "validierung", 
            "validierung": "archivierung"
        }
        
        next_status = next_status_map.get(current_status)
        if not next_status:
            return False  # Bereits abgeschlossen
            
        # Zeitstempel hinzufügen
        timestamp = f"{next_status}:{datetime.now().isoformat()}"
        case["zeitstempel"].append(timestamp)
        
        # AFM-String aktualisieren
        update_case_afm_string(case)
        
        # Speichern
        self._save_cases({"cases": cases})
        return True
    
    def create_case(self, quelle, fundstellen):
        """Neuen Case erstellen (API-ready)"""
        cases = self.get_cases()
        new_case = {
            "quelle": quelle,
            "fundstellen": fundstellen,
            "afm_string": "",
            "zeitstempel": [f"erfassung:{datetime.now().isoformat()}"]
        }
        # AFM-String generieren
        update_case_afm_string(new_case)
        
        cases.append(new_case)
        self._save_cases({"cases": cases})
        return new_case
    
    def _save_cases(self, data):
        """Cases speichern"""
        with open(self.cases_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
