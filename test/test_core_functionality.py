#!/usr/bin/env python3
"""
Umfassende Tests für AFMTool1 Kernfunktionalität
==============================================

Dieses Testskript testet die grundlegenden Module und Funktionen von AFMTool1:
- Database-Operationen (laden, speichern, Cases hinzufügen)
- AFM-String-Utilities (generieren, validieren, Zeitstempel)
- Logger-Funktionalität (protokollieren, Einträge abrufen)
- Eingabevalidierung und Fehlerbehandlung
- Edge Cases und ungültige Eingaben

Verwendung: pytest test/test_core_functionality.py -v
"""

import pytest
import json
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, mock_open

# Import der AFMTool1 Module
import sys
sys.path.append(str(Path(__file__).parent.parent))

from utils.database import (
    load_database, save_database, add_case_with_fields, 
    get_cases_count, get_last_filled_cases, get_latest_case_info
)
from utils.logger import log_action, get_log_entries
from utils.afm_utils import (
    generate_afm_string_for_case, update_case_afm_string,
    add_timestamp_to_case, get_timestamps_from_case,
    validate_afm_strings, add_new_case_with_afm
)


class TestDatabaseOperations:
    """Tests für Database-Operationen (utils/database.py)"""
    
    def setup_method(self):
        """Setup für jeden Test - temporäre Testdaten erstellen"""
        self.test_data = {
            "cases": [
                {
                    "quelle": "Test Quelle 1",
                    "fundstellen": "Test Fundstelle 1",
                    "afm_string": '{"quelle": "Test Quelle 1", "fundstellen": "Test Fundstelle 1"}'
                },
                {
                    "quelle": "Test Quelle 2", 
                    "fundstellen": "Test Fundstelle 2",
                    "kategorie": "Test Kategorie",
                    "afm_string": '{"quelle": "Test Quelle 2", "fundstellen": "Test Fundstelle 2", "kategorie": "Test Kategorie"}'
                }
            ]
        }
    
    def test_load_database_existing_file(self):
        """Test: Laden einer existierenden Datenbank"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            json.dump(self.test_data, f, ensure_ascii=False, indent=2)
            temp_path = f.name
        
        with patch('utils.database.DATABASE_PATH', temp_path):
            result = load_database()
            
        assert result == self.test_data
        assert len(result['cases']) == 2
        assert result['cases'][0]['quelle'] == "Test Quelle 1"
        
        os.unlink(temp_path)
    
    def test_load_database_nonexistent_file(self):
        """Test: Laden einer nicht-existierenden Datenbank"""
        with patch('utils.database.DATABASE_PATH', '/nonexistent/path.json'):
            result = load_database()
            
        assert result == {"cases": []}
        assert len(result['cases']) == 0
    
    def test_save_database(self):
        """Test: Speichern der Datenbank"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_path = f.name
        
        with patch('utils.database.DATABASE_PATH', temp_path):
            save_database(self.test_data)
            
        # Prüfen ob Datei korrekt gespeichert wurde
        with open(temp_path, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
            
        assert saved_data == self.test_data
        os.unlink(temp_path)
    
    def test_get_cases_count(self):
        """Test: Anzahl der Cases abrufen"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            json.dump(self.test_data, f)
            temp_path = f.name
            
        with patch('utils.database.DATABASE_PATH', temp_path):
            count = get_cases_count()
            
        assert count == 2
        os.unlink(temp_path)
    
    def test_get_cases_count_empty_database(self):
        """Test: Anzahl der Cases bei leerer Datenbank"""
        empty_data = {"cases": []}
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            json.dump(empty_data, f)
            temp_path = f.name
            
        with patch('utils.database.DATABASE_PATH', temp_path):
            count = get_cases_count()
            
        assert count == 0
        os.unlink(temp_path)
    
    def test_add_case_with_fields(self):
        """Test: Case mit Feldern hinzufügen"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            json.dump({"cases": []}, f)
            temp_path = f.name
        
        new_case = {
            "quelle": "Neue Quelle",
            "fundstellen": "Neue Fundstelle",
            "kategorie": "Neue Kategorie"
        }
        
        with patch('utils.database.DATABASE_PATH', temp_path):
            result = add_case_with_fields(new_case)
            
        # Prüfen ob Case hinzugefügt wurde
        assert 'afm_string' in result
        assert result['quelle'] == "Neue Quelle"
        
        # Prüfen ob in Datenbank gespeichert
        with open(temp_path, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
            
        assert len(saved_data['cases']) == 1
        assert saved_data['cases'][0]['quelle'] == "Neue Quelle"
        os.unlink(temp_path)
    
    def test_get_last_filled_cases(self):
        """Test: Letzte befüllte Cases abrufen"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            json.dump(self.test_data, f)
            temp_path = f.name
            
        with patch('utils.database.DATABASE_PATH', temp_path):
            # Letzter Case
            last_one = get_last_filled_cases(1)
            assert len(last_one) == 1
            assert last_one[0]['quelle'] == "Test Quelle 2"
            
            # Alle Cases
            all_cases = get_last_filled_cases(-1)
            assert len(all_cases) == 2
            
            # Letzte 2 Cases
            last_two = get_last_filled_cases(2)
            assert len(last_two) == 2
            
        os.unlink(temp_path)
    
    def test_get_latest_case_info(self):
        """Test: Detaillierte Informationen über neuesten Case"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            json.dump(self.test_data, f)
            temp_path = f.name
            
        with patch('utils.database.DATABASE_PATH', temp_path):
            info = get_latest_case_info()
            
        assert info['exists'] == True
        assert info['total_count'] == 2
        assert info['latest']['quelle'] == "Test Quelle 2"
        assert info['latest_index'] == 1
        
        os.unlink(temp_path)
    
    def test_get_latest_case_info_empty_database(self):
        """Test: Case-Info bei leerer Datenbank"""
        empty_data = {"cases": []}
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            json.dump(empty_data, f)
            temp_path = f.name
            
        with patch('utils.database.DATABASE_PATH', temp_path):
            info = get_latest_case_info()
            
        assert info['exists'] == False
        assert info['total_count'] == 0
        assert info['latest'] == None
        assert info['latest_index'] == -1
        
        os.unlink(temp_path)


class TestAFMUtils:
    """Tests für AFM-String-Utilities (utils/afm_utils.py)"""
    
    def test_generate_afm_string_for_case(self):
        """Test: AFM-String für Case generieren"""
        case_data = {
            "quelle": "Test Quelle",
            "fundstellen": "Test Fundstelle",
            "kategorie": "Test Kategorie",
            "status": "aktiv"
        }
        
        afm_string = generate_afm_string_for_case(case_data)
        
        # AFM String sollte JSON sein
        parsed = json.loads(afm_string)
        assert "quelle" in parsed
        assert "fundstellen" in parsed
        assert "kategorie" in parsed
        assert "status" in parsed
        assert parsed["quelle"] == "Test Quelle"
    
    def test_generate_afm_string_excludes_fields(self):
        """Test: AFM-String schließt bestimmte Felder aus"""
        case_data = {
            "quelle": "Test Quelle",
            "fundstellen": "Test Fundstelle",
            "afm_string": "should be excluded"
        }
        
        afm_string = generate_afm_string_for_case(case_data, exclude_fields=['afm_string'])
        parsed = json.loads(afm_string)
        
        assert "afm_string" not in parsed
        assert "quelle" in parsed
        assert "fundstellen" in parsed
    
    def test_generate_afm_string_empty_values(self):
        """Test: AFM-String ignoriert leere Werte"""
        case_data = {
            "quelle": "Test Quelle",
            "fundstellen": "",  # leerer String
            "kategorie": None,  # None Wert
            "status": "aktiv"
        }
        
        afm_string = generate_afm_string_for_case(case_data)
        parsed = json.loads(afm_string)
        
        assert "quelle" in parsed
        assert "fundstellen" not in parsed  # leerer String ausgeschlossen
        assert "kategorie" not in parsed   # None ausgeschlossen
        assert "status" in parsed
    
    def test_update_case_afm_string(self):
        """Test: AFM-String für Case aktualisieren"""
        case_data = {
            "quelle": "Test Quelle",
            "fundstellen": "Test Fundstelle"
        }
        
        updated_case = update_case_afm_string(case_data)
        
        assert 'afm_string' in updated_case
        assert updated_case['quelle'] == "Test Quelle"
        
        # AFM String sollte beide Felder enthalten
        parsed = json.loads(updated_case['afm_string'])
        assert "quelle" in parsed
        assert "fundstellen" in parsed
    
    def test_add_timestamp_to_case(self):
        """Test: Zeitstempel zu Case hinzufügen"""
        case_data = {"quelle": "Test"}
        
        # Ersten Zeitstempel hinzufügen
        result = add_timestamp_to_case(case_data, "erfassung")
        
        assert "zeitstempel" in result
        assert len(result["zeitstempel"]) == 1
        assert result["zeitstempel"][0].startswith("erfassung:")
        
        # Zweiten Zeitstempel hinzufügen
        result = add_timestamp_to_case(result, "verarbeitung")
        
        assert len(result["zeitstempel"]) == 2
        assert result["zeitstempel"][1].startswith("verarbeitung:")
    
    def test_get_timestamps_from_case(self):
        """Test: Zeitstempel aus Case extrahieren"""
        case_data = {
            "zeitstempel": [
                "erfassung:2025-07-23T10:00:00",
                "verarbeitung:2025-07-23T11:00:00"
            ]
        }
        
        timestamps = get_timestamps_from_case(case_data)
        
        assert len(timestamps) == 2
        assert timestamps[0]["type"] == "erfassung"
        assert timestamps[0]["timestamp"] == "2025-07-23T10:00:00"
        assert timestamps[1]["type"] == "verarbeitung"
        assert timestamps[1]["timestamp"] == "2025-07-23T11:00:00"
    
    def test_get_timestamps_from_case_no_timestamps(self):
        """Test: Zeitstempel extrahieren wenn keine vorhanden"""
        case_data = {"quelle": "Test"}
        timestamps = get_timestamps_from_case(case_data)
        assert timestamps == []
    
    def test_validate_afm_strings(self):
        """Test: AFM-Strings validieren"""
        test_data = {
            "cases": [
                {
                    "quelle": "Test 1",
                    "fundstellen": "Fund 1",
                    "afm_string": '{"quelle": "Test 1", "fundstellen": "Fund 1"}'
                },
                {
                    "quelle": "Test 2",
                    "fundstellen": "Fund 2", 
                    "afm_string": '{"quelle": "Test 2"}'  # fehlende fundstellen
                }
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            json.dump(test_data, f)
            temp_path = f.name
        
        results = validate_afm_strings(temp_path)
        
        assert len(results) == 2
        assert results[0]["afm_valid"] == True
        assert results[1]["afm_valid"] == False
        assert "fundstellen" in results[1]["missing_fields"]
        
        os.unlink(temp_path)


class TestLoggerFunctionality:
    """Tests für Logger-Funktionalität (utils/logger.py)"""
    
    def test_log_action(self):
        """Test: Aktion protokollieren"""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_path = Path(temp_dir) / "test.log"
            
            with patch('utils.logger.LOG_PATH', log_path):
                log_action("TEST", "Test details")
                
            # Prüfen ob Log-Datei erstellt wurde
            assert log_path.exists()
            
            # Log-Inhalt prüfen
            with open(log_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            assert "TEST" in content
            assert "Test details" in content
            assert "[" in content  # Zeitstempel-Format
    
    def test_log_action_creates_directory(self):
        """Test: Logger erstellt Verzeichnis wenn es nicht existiert"""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_path = Path(temp_dir) / "logs" / "test.log"
            
            with patch('utils.logger.LOG_PATH', log_path):
                log_action("TEST", "Test")
                
            assert log_path.parent.exists()
            assert log_path.exists()
    
    def test_get_log_entries(self):
        """Test: Log-Einträge abrufen"""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_path = Path(temp_dir) / "test.log"
            
            # Test-Log erstellen
            test_lines = [
                "[2025-07-23 10:00:00] ACTION1: Details1\n",
                "[2025-07-23 10:01:00] ACTION2: Details2\n", 
                "[2025-07-23 10:02:00] ACTION3: Details3\n"
            ]
            
            with open(log_path, 'w', encoding='utf-8') as f:
                f.writelines(test_lines)
            
            with patch('utils.logger.LOG_PATH', log_path):
                # Letzte 2 Einträge abrufen
                entries = get_log_entries(2)
                
            assert len(entries) == 2
            assert "ACTION2" in entries[0]
            assert "ACTION3" in entries[1]
    
    def test_get_log_entries_nonexistent_file(self):
        """Test: Log-Einträge abrufen wenn Datei nicht existiert"""
        with patch('utils.logger.LOG_PATH', '/nonexistent/path.log'):
            entries = get_log_entries(10)
            
        assert entries == []


class TestInputValidation:
    """Tests für Eingabevalidierung und Fehlerbehandlung"""
    
    def test_case_with_special_characters(self):
        """Test: Case mit Sonderzeichen"""
        case_data = {
            "quelle": "Österreichisches Firmenbuch",
            "fundstellen": "§123/2025 äöü ß",
            "bemerkung": "Test mit Umlauten & Symbolen"
        }
        
        afm_string = generate_afm_string_for_case(case_data)
        parsed = json.loads(afm_string)
        
        assert parsed["quelle"] == "Österreichisches Firmenbuch"
        assert parsed["fundstellen"] == "§123/2025 äöü ß"
        assert "Umlauten" in parsed["bemerkung"]
    
    def test_case_with_very_long_strings(self):
        """Test: Case mit sehr langen Strings"""
        long_string = "A" * 1000  # 1000 Zeichen
        case_data = {
            "quelle": long_string,
            "fundstellen": "Normal length"
        }
        
        afm_string = generate_afm_string_for_case(case_data)
        parsed = json.loads(afm_string)
        
        assert len(parsed["quelle"]) == 1000
        assert parsed["fundstellen"] == "Normal length"
    
    def test_case_with_only_whitespace(self):
        """Test: Case mit nur Leerzeichen"""
        case_data = {
            "quelle": "   ",  # nur Leerzeichen
            "fundstellen": "Valid content",
            "leer": ""
        }
        
        afm_string = generate_afm_string_for_case(case_data)
        parsed = json.loads(afm_string)
        
        # Leerzeichen sollten beibehalten werden, leere Strings ausgeschlossen
        assert parsed["quelle"] == "   "
        assert parsed["fundstellen"] == "Valid content"
        assert "leer" not in parsed
    
    def test_malformed_json_in_afm_string(self):
        """Test: Validierung mit fehlerhaftem JSON in AFM-String"""
        test_data = {
            "cases": [
                {
                    "quelle": "Test",
                    "afm_string": "INVALID JSON"
                }
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            json.dump(test_data, f)
            temp_path = f.name
        
        results = validate_afm_strings(temp_path)
        
        assert len(results) == 1
        assert results[0]["afm_valid"] == False
        assert "INVALID_JSON" in results[0]["missing_fields"]
        
        os.unlink(temp_path)


class TestEdgeCases:
    """Tests für Edge Cases und Grenzfälle"""
    
    def test_empty_case_data(self):
        """Test: Leere Case-Daten"""
        case_data = {}
        afm_string = generate_afm_string_for_case(case_data)
        parsed = json.loads(afm_string)
        
        assert parsed == {}
    
    def test_case_with_nested_data(self):
        """Test: Case mit verschachtelten Daten"""
        case_data = {
            "quelle": "Test",
            "details": {
                "nested": "value",
                "number": 123
            }
        }
        
        afm_string = generate_afm_string_for_case(case_data)
        parsed = json.loads(afm_string)
        
        assert parsed["quelle"] == "Test"
        assert isinstance(parsed["details"], dict)
        assert parsed["details"]["nested"] == "value"
    
    def test_case_with_mixed_data_types(self):
        """Test: Case mit gemischten Datentypen"""
        case_data = {
            "string_field": "text",
            "number_field": 42,
            "float_field": 3.14,
            "bool_field": True,
            "list_field": ["a", "b", "c"]
        }
        
        afm_string = generate_afm_string_for_case(case_data)
        parsed = json.loads(afm_string)
        
        assert parsed["string_field"] == "text"
        assert parsed["number_field"] == 42
        assert parsed["float_field"] == 3.14
        assert parsed["bool_field"] == True
        assert parsed["list_field"] == ["a", "b", "c"]
    
    def test_database_with_invalid_structure(self):
        """Test: Datenbank mit ungültiger Struktur"""
        invalid_data = {"wrong_key": []}  # Fehlt 'cases' key
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            json.dump(invalid_data, f)
            temp_path = f.name
        
        with patch('utils.database.DATABASE_PATH', temp_path):
            count = get_cases_count()
            
        assert count == 0  # Sollte 0 zurückgeben statt Fehler
        os.unlink(temp_path)


if __name__ == "__main__":
    """
    Führe alle Tests aus wenn Skript direkt aufgerufen wird
    Verwendung: python test_core_functionality.py
    """
    pytest.main([__file__, "-v", "--tb=short"])