"""
AFMTool1 Case Report Generator
Fallnummer-basierte Gruppierung mit fallnummer_verknuepfung.py
"""
import json
import datetime
from pathlib import Path
import sys

# Pfad zu utils hinzufügen
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "utils"))

try:
    from utils.fallnummer_verknuepfung import find_fallnummer_groups, get_case_summary, ensure_fallnummer, generate_hash_uuid
    FALLBACK_MODE = False
except ImportError:
    print("⚠️ Fallback: fallnummer_verknuepfung.py nicht verfügbar")
    FALLBACK_MODE = True

class CaseReporter:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.data_dir = self.project_root / "data"
        self.report_dir = Path(__file__).parent / "temp_reports"
        self.report_dir.mkdir(exist_ok=True)
        
    def load_cases(self):
        """Cases aus JSON laden"""
        db_path = self.data_dir / "cases.json"
        if not db_path.exists():
            print(f"❌ Datei nicht gefunden: {db_path}")
            return []
            
        try:
            with open(db_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                cases = data.get('cases', [])
                print(f"✅ {len(cases)} Cases geladen")
                return cases
        except Exception as e:
            print(f"❌ Fehler beim Laden: {e}")
            return []
    
    def generate_hash_uuid(self, case):
        """5-stelligen Hash aus erfassung-Zeitstempel generieren - Fallback"""
        if not FALLBACK_MODE:
            return generate_hash_uuid(case)
        
        # Fallback-Implementation
        import hashlib
        for ts in case.get('zeitstempel', []):
            if ts.startswith('erfassung:'):
                timestamp_part = ts.replace('erfassung:', '')
                hash_obj = hashlib.md5(timestamp_part.encode('utf-8'))
                short_hash = hash_obj.hexdigest()[:5].upper()
                return short_hash
        return "ERROR"
    
    def format_case_info(self, case_num, case):
        """Case-Information formatieren - Fallback für alte Funktionalität"""
        if not FALLBACK_MODE:
            return f"Fallback-Formatierung Case {case_num}"
            
        uuid_hash = self.generate_hash_uuid(case)
        fallnummer = case.get('fallnummer', 'LEER')
        quelle = case.get('quelle', 'KEINE_QUELLE')
        zeitstempel_count = len(case.get('zeitstempel', []))
        fundstellen = case.get('fundstellen', 'KEINE_FUNDSTELLEN')
        
        return f"""Case {case_num}:
  UUID: {uuid_hash}
  Fallnummer: {fallnummer}
  Quelle: {quelle}
  Fundstellen: {fundstellen}
  Zeitstempel: {zeitstempel_count} Einträge
{'-' * 50}"""
    
    def generate_case_list(self):
        """TXT-Report mit Fallnummer-Gruppierung generieren"""
        cases = self.load_cases()
        if not cases:
            return None
        
        if not FALLBACK_MODE:
            # Verwendung von fallnummer_verknuepfung.py
            groups = find_fallnummer_groups(cases)
            summary = get_case_summary(cases)
        else:
            # Fallback-Modus
            groups = {"exakte_gruppen": {}}
            summary = []
            for case in cases:
                fallnummer = case.get("fallnummer", "LEER")
                if fallnummer not in groups["exakte_gruppen"]:
                    groups["exakte_gruppen"][fallnummer] = []
                groups["exakte_gruppen"][fallnummer].append("FALLBACK")
                summary.append({
                    "uuid": "FALLBACK",
                    "fallnummer": fallnummer,
                    "quelle": case.get("quelle", "KEINE_QUELLE"),
                    "zeitstempel_count": len(case.get("zeitstempel", []))
                })
        
        # TXT-Datei erstellen
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        txt_path = self.report_dir / f"case_report_{timestamp}.txt"
        
        try:
            with open(txt_path, 'w', encoding='utf-8') as f:
                # Header
                f.write("AFMTool1 - Fallnummer-gruppierter Case Report\n")
                f.write(f"Generiert: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Anzahl Cases: {len(cases)}\n")
                f.write(f"Fallnummer-Gruppen: {len(groups['exakte_gruppen'])}\n")
                f.write("=" * 60 + "\n\n")
                
                # Gruppierte Ausgabe nach Fallnummer
                for fallnummer, hash_uuids in groups["exakte_gruppen"].items():
                    # Fallnummer-Header
                    if fallnummer.startswith("AUTO-"):
                        f.write(f"🔄 FALLNUMMER: {fallnummer} (Auto-generiert)\n")
                    else:
                        f.write(f"✅ FALLNUMMER: {fallnummer}\n")
                    f.write(f"   Anzahl Cases: {len(hash_uuids)}\n")
                    f.write(f"   UUIDs: {', '.join(hash_uuids)}\n")
                    f.write("-" * 50 + "\n")
                    
                    # Cases dieser Fallnummer auflisten
                    case_counter = 1
                    for case_info in summary:
                        if case_info["fallnummer"] == fallnummer:
                            f.write(f"  Case {case_counter}:\n")
                            f.write(f"    UUID: {case_info['uuid']}\n")
                            f.write(f"    Quelle: {case_info['quelle']}\n")
                            f.write(f"    Zeitstempel: {case_info['zeitstempel_count']} Einträge\n")
                            f.write(f"    {'-' * 40}\n")
                            case_counter += 1
                    
                    f.write("\n")
                
                # Footer mit Statistiken
                f.write("ZUSAMMENFASSUNG:\n")
                f.write("=" * 30 + "\n")
                f.write(f"Gesamt Cases: {len(cases)}\n")
                f.write(f"Fallnummer-Gruppen: {len(groups['exakte_gruppen'])}\n")
                
                # Gruppierungsstatistik
                single_cases = sum(1 for uuids in groups["exakte_gruppen"].values() if len(uuids) == 1)
                multi_cases = len(groups["exakte_gruppen"]) - single_cases
                f.write(f"Einzelne Cases: {single_cases}\n")
                f.write(f"Gruppierte Fallnummern: {multi_cases}\n")
                
                f.write(f"\nReport Ende - Datei: {txt_path.name}\n")
            
            print(f"✅ Fallnummer-gruppierter Report erstellt: {txt_path.name}")
            return txt_path
            
        except Exception as e:
            print(f"❌ Fehler beim Schreiben: {e}")
            return None

def main():
    """Hauptfunktion"""
    print("=== AFMTool1 Fallnummer-gruppierter Case Report ===")
    if FALLBACK_MODE:
        print("⚠️ Läuft im Fallback-Modus ohne fallnummer_verknuepfung.py")
    else:
        print("✅ Verwendet fallnummer_verknuepfung.py für Gruppierung")
    
    reporter = CaseReporter()
    report_path = reporter.generate_case_list()
    
    if report_path:
        print(f"📄 Fallnummer-gruppierter Report verfügbar: {report_path}")
    else:
        print("❌ Report konnte nicht erstellt werden")

if __name__ == "__main__":
    main()
