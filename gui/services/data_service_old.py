"""
Data Service Layer für AFMTool1
Pure AFM-String basierte Datenoperationen
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
        
        # Session-basierte lokale Dateien in temporärem Verzeichnis
        import tempfile
        import os
        
        # Temporäres Verzeichnis für diese Session
        self.session_temp_dir = Path(tempfile.gettempdir()) / "afmtool_session" / f"session_{os.getpid()}"
        self.session_temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Lokale AFM-Datei in Session-Verzeichnis
        self.local_afm_file = self.session_temp_dir / "afm_strings_local.json"
        
        # Permanente Verzeichnisse
        self.exports_dir.mkdir(exist_ok=True)
        
        self.export_service = AFMExportService(cases_file, self.exports_dir)
        
        print(f"📂 [PURE AFM] Session-Verzeichnis: {self.session_temp_dir}")
        print(f"💾 [PURE AFM] AFM Storage: {self.pure_storage.storage_file}")
        
        # Bei Initialisierung: Pure AFM Daten laden
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
            success, result = self.export_service.create_export()
            if not success:
                print(f"❌ [EXPORT] Export-Fehler: {result}")
                return
            
            print(f"✅ [EXPORT] AFM-Export erstellt: {result}")
                
            # 2. Export-Daten in lokale Datei kopieren
            export_cases = self.export_service.load_export_cases()
            if export_cases:
                self._save_local_afm_data(export_cases)
                print(f"✅ [IMPORT] Lokale AFM-Datei initialisiert ({len(export_cases)} Cases)")
            else:
                print("⚠️ [IMPORT] Keine Export-Daten gefunden")
                
        except Exception as e:
            print(f"⚠️ Initialisierung fehlgeschlagen: {e}")
    
    def get_cases(self):
        """Cases laden - Priorität: Lokale AFM-Datei → Fallback: Original"""
        try:
            # Priorität 1: Aus lokaler AFM-Datei laden
            if self.local_afm_file.exists():
                with open(self.local_afm_file, 'r', encoding='utf-8') as f:
                    local_data = json.load(f)
                    return local_data.get("cases", [])
                    
            # Fallback: Direkt aus cases.json laden  
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
        """Cases speichern - nur in lokale AFM-Datei (Session-basiert) mit AFM-String-Schutz"""
        try:
            cases = data.get("cases", [])
            
            # AUTO-SCHUTZ: AFM-Strings regenerieren falls fehlend
            self._ensure_afm_strings(cases)
            
            # Nur lokale AFM-Datei aktualisieren
            self._save_local_afm_data(cases)
            print(f"💾 [SESSION] {len(cases)} Cases in Session-Cache gespeichert")
                
        except Exception as e:
            print(f"⚠️ Session-Speicher-Fehler: {e}")
    
    def _ensure_afm_strings(self, cases):
        """Stellt sicher, dass alle Cases AFM-Strings haben - AUTO-REPARATUR"""
        from utils.afm_utils import update_case_afm_string
        
        missing_count = 0
        for i, case in enumerate(cases):
            if not case.get("afm_string"):
                cases[i] = update_case_afm_string(case)
                missing_count += 1
        
        if missing_count > 0:
            print(f"🔧 [AUTO-FIX] {missing_count} AFM-Strings automatisch regeneriert")
    
    def _save_local_afm_data(self, cases):
        """Speichert Cases in lokale AFM-Datei"""
        try:
            print(f"💾 [SAVE] Speichere {len(cases)} Cases in lokale AFM-Datei...")
            
            # AFM-Strings aus Cases extrahieren
            afm_strings = []
            for case in cases:
                afm_string = case.get("afm_string")
                if afm_string:
                    afm_strings.append(afm_string)
            
            print(f"📝 [PROCESS] {len(afm_strings)} AFM-Strings extrahiert")
            
            # Lokale AFM-Datei erstellen
            local_data = {
                "last_update": datetime.now().isoformat(),
                "case_count": len(cases),
                "cases": cases,  # Vollständige Cases für GUI
                "afm_strings": afm_strings  # Nur AFM-Strings für Export
            }
            
            with open(self.local_afm_file, 'w', encoding='utf-8') as f:
                json.dump(local_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ [SAVE] Lokale AFM-Datei erfolgreich erstellt: {self.local_afm_file.name}")
                
        except Exception as e:
            print(f"⚠️ Lokale Speicherung fehlgeschlagen: {e}")
    
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
    
    def refresh_export(self):
        """Datenabgleich mit visueller Konfliktauflösung"""
        try:
            print("🔄 [SYNC] Starte Datenabgleich...")
            
            # 1. Aktuelle lokale Daten laden
            local_cases = self.get_cases()
            print(f"📂 [LOAD] Lokale Daten geladen: {len(local_cases)} Cases")
            
            # 2. Neuen Export aus cases.json erstellen
            success, result = self.export_service.create_export()
            if not success:
                print(f"❌ [EXPORT] Export fehlgeschlagen: {result}")
                return False, f"Export fehlgeschlagen: {result}"
            
            print(f"✅ [EXPORT] Server-Export erstellt: {result}")
            
            # 3. Server-Daten aus Export laden
            server_cases = self.export_service.load_export_cases()
            if not server_cases:
                print("❌ [IMPORT] Keine Server-Daten gefunden")
                return False, "Keine Server-Daten gefunden"
            
            print(f"📥 [IMPORT] Server-Daten geladen: {len(server_cases)} Cases")
            
            # 4. Konflikte erkennen
            conflicts = self._detect_conflicts(local_cases, server_cases)
            
            if conflicts:
                print(f"⚠️ [CONFLICT] {len(conflicts)} Konflikte erkannt - Starte visuelle Auflösung")
                # Konflikte visuell lösen über GUI
                return self._resolve_conflicts_visually(conflicts, local_cases, server_cases)
            else:
                print("✅ [SYNC] Keine Konflikte gefunden - Übernehme Server-Daten")
                # Keine Konflikte - Server-Daten übernehmen
                self._save_local_afm_data(server_cases)
                print(f"💾 [SAVE] Lokale Daten aktualisiert: {len(server_cases)} Cases")
                return True, f"Daten synchronisiert: {len(server_cases)} Cases"
                
        except Exception as e:
            print(f"❌ [ERROR] Abgleich fehlgeschlagen: {str(e)}")
            return False, f"Abgleich fehlgeschlagen: {str(e)}"
    
    def _detect_conflicts(self, local_cases, server_cases):
        """Erkennt Konflikte zwischen lokalen und Server-Daten"""
        conflicts = []
        
        # UUID-basierte Zuordnung
        local_dict = {case.get("uuid"): case for case in local_cases if case.get("uuid")}
        server_dict = {case.get("uuid"): case for case in server_cases if case.get("uuid")}
        
        for uuid, local_case in local_dict.items():
            if uuid in server_dict:
                server_case = server_dict[uuid]
                
                # Zeitstempel vergleichen - letzter Timestamp entscheidet
                local_last = self._get_last_timestamp(local_case)
                server_last = self._get_last_timestamp(server_case)
                
                if local_last != server_last:
                    conflicts.append({
                        "uuid": uuid,
                        "type": "modified",
                        "local": local_case,
                        "server": server_case,
                        "local_last": local_last,
                        "server_last": server_last
                    })
        
        return conflicts
    
    def _get_last_timestamp(self, case):
        """Gibt den letzten Zeitstempel eines Cases zurück"""
        timestamps = case.get("zeitstempel", [])
        return timestamps[-1] if timestamps else ""
    
    def _resolve_conflicts_visually(self, conflicts, local_cases, server_cases):
        """Löst Konflikte visuell über GUI-Tabelle"""
        print(f"🎯 [CONFLICT] Bereite visuelle Konfliktauflösung vor ({len(conflicts)} Konflikte)")
        
        # Konflikte markieren und Benutzer entscheiden lassen
        conflict_data = {
            "conflicts": conflicts,
            "local_cases": local_cases,
            "server_cases": server_cases,
            "resolved": False
        }
        
        # Konflikt-Status für GUI setzen
        self.conflict_data = conflict_data
        print("🖥️ [GUI] Konflikte an GUI übertragen - Warte auf Benutzeraktion")
        
        return "conflicts", f"{len(conflicts)} Konflikte gefunden - Bitte in Tabelle lösen"
    
    def sync_session_data(self):
        """Session-Datenabgleich ohne Shutdown - Gleiche Logik wie sync_and_shutdown aber ohne Cleanup"""
        try:
            print("🔄 [SYNC] Starte Session-Datenabgleich...")
            
            # Session-Daten nur ERGÄNZEN, nicht überschreiben
            local_cases = self.get_cases()
            if local_cases:
                print(f"📤 [MERGE] Ergänze {len(local_cases)} Session-Cases in cases.json")
                
                # Original cases.json laden
                original_cases = []
                if os.path.exists(self.cases_file):
                    with open(self.cases_file, 'r', encoding='utf-8') as f:
                        original_data = json.load(f)
                        original_cases = original_data.get("cases", [])
                
                # Session-Cases mit Original-Cases zusammenführen (nach erfassung-Zeitstempel)
                merged_cases = self._merge_cases_safely(original_cases, local_cases)
                
                with open(self.cases_file, 'w', encoding='utf-8') as f:
                    json.dump({"cases": merged_cases}, f, indent=2, ensure_ascii=False)
                print(f"✅ [MERGE] {len(merged_cases)} Cases erfolgreich zusammengeführt")
                
                # Session-Daten neu initialisieren mit aktualisierten Daten
                self._initialize_local_data()
                
                return True, f"Session synchronisiert: {len(merged_cases)} Cases"
            else:
                return False, "Keine Session-Daten zum Synchronisieren gefunden"
            
        except Exception as e:
            print(f"❌ [ERROR] Session-Sync fehlgeschlagen: {e}")
            return False, f"Session-Sync fehlgeschlagen: {e}"
    
    def sync_and_shutdown(self):
        """Synchronisation beim Beenden der GUI mit Session-Cleanup - ERGÄNZUNG statt Überschreibung"""
        try:
            # Zuerst Session-Sync (gleiche Logik wie Button)
            sync_result = self.sync_session_data()
            
            # Dann Session-Cleanup
            self._cleanup_session_data()
            print("🧹 [CLEANUP] Session bereinigt")
            
            return sync_result[0]
            
        except Exception as e:
            print(f"❌ [SHUTDOWN] Synchronisation fehlgeschlagen: {e}")
            # Trotzdem Session-Cleanup versuchen
            try:
                self._cleanup_session_data()
            except Exception as cleanup_e:
                print(f"❌ [CLEANUP] Session-Bereinigung fehlgeschlagen: {cleanup_e}")
            return False
    
    def _merge_cases_safely(self, original_cases, session_cases):
        """Sichere Zusammenführung von Original- und Session-Daten nach erfassung-Zeitstempel mit AFM-String-Schutz"""
        from utils.afm_utils import update_case_afm_string
        
        # Dictionary für schnelleren Zugriff nach erfassung-Zeitstempel
        original_by_timestamp = {}
        for case in original_cases:
            # AUTO-SCHUTZ: AFM-String regenerieren falls fehlend
            if not case.get("afm_string"):
                case = update_case_afm_string(case)
                
            timestamps = case.get("zeitstempel", [])
            if timestamps:
                erfassung_ts = next((ts for ts in timestamps if ts.startswith("erfassung:")), None)
                if erfassung_ts:
                    original_by_timestamp[erfassung_ts] = case
        
        merged = []
        
        # Alle Session-Cases hinzufügen (überschreiben Original bei gleichem erfassung-Zeitstempel)
        for session_case in session_cases:
            # AUTO-SCHUTZ: AFM-String regenerieren falls fehlend
            if not session_case.get("afm_string"):
                session_case = update_case_afm_string(session_case)
                
            timestamps = session_case.get("zeitstempel", [])
            if timestamps:
                erfassung_ts = next((ts for ts in timestamps if ts.startswith("erfassung:")), None)
                if erfassung_ts:
                    # Session-Case überschreibt Original bei gleichem erfassung-Zeitstempel
                    original_by_timestamp[erfassung_ts] = session_case
        
        # Alle Cases (Original + Session-Updates) zusammenführen
        merged = list(original_by_timestamp.values())
        
        print(f"🔄 [MERGE] Original: {len(original_cases)}, Session: {len(session_cases)}, Zusammengeführt: {len(merged)}")
        return merged
    
    def _cleanup_session_data(self):
        """Löscht Session-spezifische temporäre Dateien"""
        try:
            if self.local_afm_file.exists():
                self.local_afm_file.unlink()
                print(f"🗑️ [CLEANUP] Session-Datei gelöscht: {self.local_afm_file.name}")
            
            # Gesamtes Session-Verzeichnis löschen
            if self.session_temp_dir.exists():
                import shutil
                shutil.rmtree(self.session_temp_dir)
                print(f"🗑️ [CLEANUP] Session-Verzeichnis gelöscht: {self.session_temp_dir}")
            
            # Optional: Auch alte Export-Dateien bereinigen (älter als 24h)
            self._cleanup_old_session_exports()
            
        except Exception as e:
            print(f"⚠️ [CLEANUP] Session-Cleanup fehlgeschlagen: {e}")
    
    def _cleanup_old_session_exports(self):
        """Bereinigt alte Export-Dateien (älter als 24h)"""
        try:
            import time
            current_time = time.time()
            
            for export_file in self.exports_dir.glob("afm_export_*.json"):
                file_age = current_time - export_file.stat().st_mtime
                
                # Dateien älter als 24 Stunden löschen
                if file_age > 86400:  # 24 * 60 * 60 Sekunden
                    export_file.unlink()
                    print(f"🗑️ [CLEANUP] Alter Export gelöscht: {export_file.name}")
                    
        except Exception as e:
            print(f"⚠️ [CLEANUP] Export-Bereinigung fehlgeschlagen: {e}")
    
    def get_export_status(self):
        """Status des neuesten Exports"""
        try:
            latest_export = self.export_service.get_latest_export()
            if not latest_export:
                return "Kein Export vorhanden"
            
            # Zeitstempel der Export-Datei
            import os
            timestamp = datetime.fromtimestamp(os.path.getmtime(latest_export))
            now = datetime.now()
            
            # Zeitdifferenz berechnen
            diff = now - timestamp
            if diff.total_seconds() < 3600:  # < 1 Stunde
                status = "✅ Aktuell"
            elif diff.total_seconds() < 7200:  # < 2 Stunden
                status = "⚠️ 1h alt"
            else:
                hours = int(diff.total_seconds() / 3600)
                status = f"⚠️ {hours}h alt"
            
            return f"{status} ({timestamp.strftime('%H:%M:%S')})"
            
        except Exception:
            return "Status unbekannt"
