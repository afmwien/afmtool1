"""
AFM Pure String System - Single Source of Truth Implementation
"""
import json
import base64
from datetime import datetime
from pathlib import Path

class AFMPureStorage:
    """AFM-String basierte Speicherung ohne redundante Case-Daten"""
    
    def __init__(self, storage_file):
        self.storage_file = Path(storage_file)
        self.storage_file.parent.mkdir(exist_ok=True)
    
    def _simplify_timestamp(self, full_timestamp):
        """Vereinfacht Zeitstempel: 2025-07-24T16:27:16.960695"""
        if ":" in full_timestamp and len(full_timestamp.split(":")) >= 3:
            parts = full_timestamp.split(":")
            return f"{parts[0]}:{parts[1]}"
        return full_timestamp
    
    def _encrypt_afm_string(self, afm_string):
        """Verschlüsselt AFM-String (Base64 Platzhalter)"""
        return base64.b64encode(afm_string.encode('utf-8')).decode('utf-8')
    
    def _decrypt_afm_string(self, encrypted_string):
        """Entschlüsselt AFM-String"""
        try:
            return base64.b64decode(encrypted_string).decode('utf-8')
        except:
            return encrypted_string
    
    def convert_case_to_pure_afm(self, case_data):
        """Konvertiert Case zu Pure AFM-String mit vereinfachten Zeitstempeln"""
        # Zeitstempel vereinfachen
        simplified_case = case_data.copy()
        if 'zeitstempel' in simplified_case:
            simplified_case['zeitstempel'] = [
                self._simplify_timestamp(ts) for ts in simplified_case['zeitstempel']
            ]
        
        # AFM-String ohne afm_string Feld selbst
        afm_data = {k: v for k, v in simplified_case.items() if k != 'afm_string'}
        return json.dumps(afm_data, ensure_ascii=False, sort_keys=True)
    
    def parse_afm_string_to_case(self, afm_string):
        """Parst AFM-String zurück zu Case-Daten"""
        try:
            decrypted = self._decrypt_afm_string(afm_string)
            return json.loads(decrypted)
        except:
            return None
    
    def save_pure_afm_data(self, cases):
        """Speichert nur AFM-Strings + Metadaten"""
        afm_strings = []
        erfassung_timestamps = []
        
        for case in cases:
            # AFM-String generieren
            pure_afm = self.convert_case_to_pure_afm(case)
            encrypted_afm = self._encrypt_afm_string(pure_afm)
            afm_strings.append(encrypted_afm)
            
            # Erfassung-Zeitstempel extrahieren
            timestamps = case.get('zeitstempel', [])
            erfassung_ts = next((ts for ts in timestamps if ts.startswith('erfassung:')), '')
            if erfassung_ts:
                erfassung_ts = self._simplify_timestamp(erfassung_ts)
            erfassung_timestamps.append(erfassung_ts)
        
        # Pure Storage Format
        pure_data = {
            "format": "afm_pure_v1.0",
            "created": datetime.now().isoformat(),
            "case_count": len(afm_strings),
            "afm_strings": afm_strings,
            "erfassung_timestamps": erfassung_timestamps
        }
        
        with open(self.storage_file, 'w', encoding='utf-8') as f:
            json.dump(pure_data, f, indent=2, ensure_ascii=False)
    
    def load_pure_afm_data(self):
        """Lädt AFM-Strings und rekonstruiert Cases"""
        try:
            with open(self.storage_file, 'r', encoding='utf-8') as f:
                pure_data = json.load(f)
            
            cases = []
            afm_strings = pure_data.get('afm_strings', [])
            
            for afm_string in afm_strings:
                case = self.parse_afm_string_to_case(afm_string)
                if case:
                    cases.append(case)
            
            return cases
        except:
            return []
