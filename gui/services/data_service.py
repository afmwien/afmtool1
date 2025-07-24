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
        """Case zum nächsten Status weiterschalten (nur bis Freigegeben)"""
        from utils.unique_timestamps import add_workflow_timestamp
        
        cases = self.get_cases()
        if case_index >= len(cases):
            return False
            
        case = cases[case_index]
        current_status = self.get_case_status(case)
        
        # Status-Mapping für nächsten Schritt (ohne archivierung - nur bis validierung)
        next_status_map = {
            "erfassung": "verarbeitung",
            "verarbeitung": "validierung"
            # "validierung" hat keinen nächsten Status mehr in der manuellen Bearbeitung
        }
        
        next_status = next_status_map.get(current_status)
        if not next_status:
            return False  # Bereits bei Freigegeben oder darüber
            
        # Eindeutigen Zeitstempel hinzufügen
        success, updated_case, error = add_workflow_timestamp(case, next_status)
        if not success:
            return False  # Zeitstempel-Konflikt
        
        # AFM-String aktualisieren
        update_case_afm_string(updated_case)
        
        # Speichern
        cases[case_index] = updated_case
        self._save_cases({"cases": cases})
        return True
    
    def retreat_case_status(self, case_index):
        """Case zum vorherigen Status zurückschalten (nur bis NEU)"""
        cases = self.get_cases()
        if case_index >= len(cases):
            return False
            
        case = cases[case_index]
        current_status = self.get_case_status(case)
        
        # Status-Mapping für vorherigen Schritt (ohne archivierung)
        previous_status_map = {
            "verarbeitung": "erfassung",
            "validierung": "verarbeitung"
            # "archivierung" sollte nicht manuell zurückgesetzt werden können
        }
        
        previous_status = previous_status_map.get(current_status)
        if not previous_status:
            return False  # Bereits am Anfang oder bei archivierung
            
        # Letzten entsprechenden Zeitstempel entfernen
        timestamps = case["zeitstempel"]
        # Alle Zeitstempel des aktuellen Status entfernen
        case["zeitstempel"] = [ts for ts in timestamps if not ts.startswith(f"{current_status}:")]
        
        # AFM-String aktualisieren
        update_case_afm_string(case)
        
        # Speichern
        self._save_cases({"cases": cases})
        return True
    
    def create_case(self, quelle, fundstellen):
        """Neuen Case erstellen (API-ready)"""
        from utils.unique_timestamps import save_case_with_validation
        
        new_case = {
            "quelle": quelle,
            "fundstellen": fundstellen,
            "afm_string": "",
            "zeitstempel": []
        }
        
        # Case mit Validierung speichern
        success, validated_case, error = save_case_with_validation(new_case)
        if not success:
            raise ValueError(f"Zeitstempel-Validierung fehlgeschlagen: {error}")
        
        # AFM-String generieren
        update_case_afm_string(validated_case)
        
        cases = self.get_cases()
        cases.append(validated_case)
        self._save_cases({"cases": cases})
        return validated_case
    
    def create_empty_case(self):
        """Leeren Case für manuelle Eingabe erstellen"""
        from utils.unique_timestamps import save_case_with_validation
        
        # Erst alle wirklich leeren Cases bereinigen
        self.cleanup_empty_cases()
        
        new_case = {
            "quelle": "",
            "fundstellen": "",
            "afm_string": "",
            "zeitstempel": []
        }
        
        # Case mit Validierung erstellen
        success, validated_case, error = save_case_with_validation(new_case)
        if not success:
            raise ValueError(f"Zeitstempel-Validierung fehlgeschlagen: {error}")
        
        # Leeren AFM-String setzen
        validated_case["afm_string"] = ""
        
        cases = self.get_cases()
        cases.append(validated_case)
        self._save_cases({"cases": cases})
        
        # Index des neuen Cases zurückgeben
        return len(cases) - 1
    
    def cleanup_empty_cases(self):
        """Entfernt alle Cases mit leeren quelle UND fundstellen Feldern"""
        cases = self.get_cases()
        
        # Nur Cases behalten die mindestens ein gefülltes Feld haben
        cleaned_cases = [
            case for case in cases 
            if case.get('quelle', '').strip() or case.get('fundstellen', '').strip()
        ]
        
        # Nur speichern wenn sich was geändert hat
        if len(cleaned_cases) != len(cases):
            self._save_cases({"cases": cleaned_cases})
    
    def _save_cases(self, data):
        """Cases speichern"""
        with open(self.cases_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def update_case(self, case_index, updates):
        """Case aktualisieren"""
        cases = self.get_cases()
        if case_index >= len(cases):
            return False
            
        case = cases[case_index]
        
        # Updates anwenden
        for key, value in updates.items():
            case[key] = value
        
        # Speichern
        self._save_cases({"cases": cases})
        return True
    
    def regenerate_afm_string(self, case_index):
        """AFM-String für einen Case neu generieren"""
        cases = self.get_cases()
        if case_index >= len(cases):
            return False
            
        case = cases[case_index]
        update_case_afm_string(case)
        
        # Speichern
        self._save_cases({"cases": cases})
        return True
    
    def delete_case(self, case_index):
        """Case komplett löschen"""
        cases = self.get_cases()
        if case_index >= len(cases):
            return False, None
            
        # Case aus Liste entfernen
        deleted_case = cases.pop(case_index)
        
        # Speichern
        self._save_cases({"cases": cases})
        return True, deleted_case
    
    def is_first_edit(self, case_index):
        """Prüfen ob ein Case das erste Mal bearbeitet wird"""
        cases = self.get_cases()
        if case_index >= len(cases):
            return False
            
        case = cases[case_index]
        current_status = self.get_case_status(case)
        
        # Case ist bei "erfassung" und hat nur einen Zeitstempel
        return (current_status == "erfassung" and 
                len(case.get("zeitstempel", [])) == 1 and
                case.get("zeitstempel", [""])[0].startswith("erfassung:"))
