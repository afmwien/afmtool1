"""
Logging-Funktionen für AFMTool1
"""
import datetime

LOG_PATH = "data/afmtool.log"

def log_action(action, details=""):
    """Aktion in Log-Datei protokollieren"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {action}: {details}\n"
    
    with open(LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(log_entry)

def get_log_entries(lines=10):
    """Letzte Log-Einträge abrufen"""
    try:
        with open(LOG_PATH, 'r', encoding='utf-8') as f:
            return f.readlines()[-lines:]
    except FileNotFoundError:
        return []
