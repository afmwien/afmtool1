"""
UUID-basierte Zeitstempel-Generierung für AFMTool1
Garantiert eindeutige Zeitstempel auch bei parallelen Imports
"""
import uuid
import datetime
import json
import re

def generate_unique_timestamp(timestamp_type="erfassung"):
    """
    Generiert eindeutigen Zeitstempel mit UUID
    
    Args:
        timestamp_type (str): Art des Zeitstempels
        
    Returns:
        str: Eindeutiger Zeitstempel im Format "typ:TIMESTAMP:UUID"
    """
    current_timestamp = datetime.datetime.now().isoformat()
    unique_id = str(uuid.uuid4())
    
    return f"{timestamp_type}:{current_timestamp}:{unique_id}"

def validate_timestamp_uniqueness(timestamps):
    """
    Prüft Eindeutigkeit aller Zeitstempel
    
    Args:
        timestamps (list): Liste von Zeitstempel-Strings
        
    Returns:
        dict: Validierungsergebnis
    """
    unique_timestamps = set()
    duplicates = []
    
    for ts in timestamps:
        if ts in unique_timestamps:
            duplicates.append(ts)
        unique_timestamps.add(ts)
    
    return {
        "is_unique": len(duplicates) == 0,
        "duplicates": duplicates,
        "total_count": len(timestamps),
        "unique_count": len(unique_timestamps)
    }

def _extract_erfassung_timestamp(timestamps):
    """
    Extrahiert erfassung-Zeitstempel
    
    Args:
        timestamps (list): Liste von Zeitstempeln
        
    Returns:
        str or None: Erfassung-Zeitstempel oder None
    """
    for ts in timestamps:
        if ts.startswith("erfassung:"):
            return ts
    return None

def _validate_immutable_timestamps(existing_case, updated_case):
    """
    Validiert unveränderliche Zeitstempel
    
    Args:
        existing_case (dict): Bestehender Case
        updated_case (dict): Aktualisierter Case
        
    Returns:
        tuple: (is_valid: bool, error_message: str)
    """
    existing_timestamps = existing_case.get("zeitstempel", [])
    updated_timestamps = updated_case.get("zeitstempel", [])
    
    # Erfassung-Zeitstempel darf nicht geändert werden
    existing_erfassung = _extract_erfassung_timestamp(existing_timestamps)
    updated_erfassung = _extract_erfassung_timestamp(updated_timestamps)
    
    if existing_erfassung and updated_erfassung:
        if existing_erfassung != updated_erfassung:
            return False, f"Erfassung-Zeitstempel darf nicht geändert werden: {existing_erfassung}"
    
    return True, ""

def save_case_with_validation(case_data, existing_case=None):
    """
    Speichert Case mit Zeitstempel-Validierung
    
    Args:
        case_data (dict): Case-Daten
        existing_case (dict, optional): Bestehender Case für Update
        
    Returns:
        tuple: (success: bool, case: dict, error: str)
    """
    try:
        # Bei Updates: Zeitstempel-Unveränderlichkeit prüfen
        if existing_case:
            is_valid, error = _validate_immutable_timestamps(existing_case, case_data)
            if not is_valid:
                return False, {}, error
        
        # Bei neuen Cases: Erfassung-Zeitstempel hinzufügen
        if not existing_case:
            if "zeitstempel" not in case_data:
                case_data["zeitstempel"] = []
            
            # Nur hinzufügen wenn noch kein erfassung-Zeitstempel existiert
            if not _extract_erfassung_timestamp(case_data["zeitstempel"]):
                unique_erfassung = generate_unique_timestamp("erfassung")
                case_data["zeitstempel"].append(unique_erfassung)
        
        # Eindeutigkeit aller Zeitstempel prüfen
        validation = validate_timestamp_uniqueness(case_data.get("zeitstempel", []))
        if not validation["is_unique"]:
            return False, {}, f"Duplikate Zeitstempel gefunden: {validation['duplicates']}"
        
        return True, case_data, ""
        
    except Exception as e:
        return False, {}, f"Validierungsfehler: {str(e)}"

def add_workflow_timestamp(case_data, timestamp_type):
    """
    Fügt Workflow-Zeitstempel hinzu (verarbeitung, validierung, archivierung)
    
    Args:
        case_data (dict): Case-Daten
        timestamp_type (str): Art des Zeitstempels
        
    Returns:
        tuple: (success: bool, updated_case: dict, error: str)
    """
    try:
        if "zeitstempel" not in case_data:
            case_data["zeitstempel"] = []
        
        # Neuen eindeutigen Zeitstempel generieren
        unique_timestamp = generate_unique_timestamp(timestamp_type)
        case_data["zeitstempel"].append(unique_timestamp)
        
        # Eindeutigkeit prüfen
        validation = validate_timestamp_uniqueness(case_data["zeitstempel"])
        if not validation["is_unique"]:
            # Letzten Zeitstempel entfernen bei Konflikt
            case_data["zeitstempel"].pop()
            return False, case_data, f"Zeitstempel-Konflikt bei {timestamp_type}"
        
        return True, case_data, ""
        
    except Exception as e:
        return False, case_data, f"Fehler beim Hinzufügen von {timestamp_type}: {str(e)}"
