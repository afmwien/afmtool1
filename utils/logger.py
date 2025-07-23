"""
Logging-Funktionen für AFMTool1
"""
import datetime
from pathlib import Path

# Log-Pfad relativ zum Projekt-Root
PROJECT_ROOT = Path(__file__).parent.parent
LOG_PATH = PROJECT_ROOT / "logs" / "afmtool.log"

def log_action(action, details=""):
    """Aktion in Log-Datei protokollieren"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {action}: {details}\n"
    
    # Logs-Verzeichnis erstellen falls es nicht existiert
    LOG_PATH.parent.mkdir(exist_ok=True)
    
    with open(LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(log_entry)

def get_log_entries(lines=10):
    """Letzte Log-Einträge abrufen"""
    try:
        with open(LOG_PATH, 'r', encoding='utf-8') as f:
            return f.readlines()[-lines:]
    except FileNotFoundError:
        return []
