# AFMTool1 Test-Dokumentation

## Übersicht

Dieses Verzeichnis enthält umfassende Tests für die AFMTool1 Kernfunktionalität. Die Tests sind darauf ausgelegt, alle grundlegenden Module und Funktionen zu validieren und eine solide Basis für die Entwicklung und Wartung zu bieten.

## Test-Dateien

### `test_core_functionality.py`
**Haupttest-Datei mit umfassender Abdeckung der Kernfunktionalität**

**Getestete Module:**
- 🗃️ **Database-Operationen** (`utils/database.py`)
- 🔧 **AFM-String-Utilities** (`utils/afm_utils.py`) 
- 📝 **Logger-Funktionalität** (`utils/logger.py`)
- ✅ **Eingabevalidierung & Edge Cases**

**Test-Kategorien:**
- `TestDatabaseOperations` - 9 Tests für Datenbank-Funktionen
- `TestAFMUtils` - 8 Tests für AFM-String-Utilities
- `TestLoggerFunctionality` - 4 Tests für Logging
- `TestInputValidation` - 4 Tests für Eingabevalidierung
- `TestEdgeCases` - 4 Tests für Grenzfälle

**Gesamt: 29 Tests**

### `test_report_function.py`
**Bestehende Tests für Report-Funktionalität** (teilweise übersprungen aufgrund GUI-Abhängigkeiten)

## Verwendung

### Schnellstart
```bash
# Alle Kerntests ausführen
python run_core_tests.py

# Mit ausführlicher Ausgabe
python run_core_tests.py --verbose

# Direkt mit pytest
python -m pytest test/test_core_functionality.py -v
```

### Alle Tests ausführen
```bash
# Alle Tests im test/ Verzeichnis
python -m pytest test/ -v

# Nur Kerntests
python -m pytest test/test_core_functionality.py -v
```

### Spezifische Test-Klassen
```bash
# Nur Database-Tests
python -m pytest test/test_core_functionality.py::TestDatabaseOperations -v

# Nur AFM-Utils-Tests  
python -m pytest test/test_core_functionality.py::TestAFMUtils -v

# Nur Logger-Tests
python -m pytest test/test_core_functionality.py::TestLoggerFunctionality -v
```

### Einzelne Tests
```bash
# Spezifischer Test
python -m pytest test/test_core_functionality.py::TestDatabaseOperations::test_load_database_existing_file -v
```

## Getestete Funktionalität im Detail

### Database-Operationen (`utils/database.py`)
- ✅ `load_database()` - Laden existierender und nicht-existierender Datenbanken
- ✅ `save_database()` - Speichern von Datenbank-Daten
- ✅ `add_case_with_fields()` - Hinzufügen neuer Cases mit AFM-String-Generierung
- ✅ `get_cases_count()` - Anzahl Cases abrufen (auch bei leerer DB)
- ✅ `get_last_filled_cases()` - Letzte Cases abrufen (verschiedene Parameter)
- ✅ `get_latest_case_info()` - Detaillierte Case-Informationen

### AFM-String-Utilities (`utils/afm_utils.py`)
- ✅ `generate_afm_string_for_case()` - AFM-String-Generierung
- ✅ Ausschluss bestimmter Felder
- ✅ Behandlung leerer Werte (None, leere Strings)
- ✅ `update_case_afm_string()` - AFM-String-Update
- ✅ `add_timestamp_to_case()` - Zeitstempel hinzufügen
- ✅ `get_timestamps_from_case()` - Zeitstempel extrahieren
- ✅ `validate_afm_strings()` - AFM-String-Validierung

### Logger-Funktionalität (`utils/logger.py`)
- ✅ `log_action()` - Aktionen protokollieren
- ✅ Automatische Verzeichnis-Erstellung
- ✅ `get_log_entries()` - Log-Einträge abrufen
- ✅ Behandlung nicht-existierender Log-Dateien

### Eingabevalidierung & Edge Cases
- ✅ **Sonderzeichen**: Umlaute, Symbole (§, &, äöüß)
- ✅ **Lange Strings**: Tests mit 1000+ Zeichen
- ✅ **Leerzeichen**: Nur Whitespace vs. leere Strings
- ✅ **Fehlerhaftes JSON**: Ungültige AFM-Strings
- ✅ **Verschachtelte Daten**: Objekte in Cases
- ✅ **Gemischte Datentypen**: String, Number, Boolean, Array
- ✅ **Ungültige Strukturen**: Fehlerhafte Datenbank-Formate

## Test-Prinzipien

### Isolation
Jeder Test verwendet temporäre Dateien und Mock-Objekte, um Isolation zu gewährleisten. Keine Tests beeinflussen die Produktions-Datenbank.

### Realitätsnähe
Tests verwenden realistische Daten, die der tatsächlichen Nutzung entsprechen (österreichische Register, Umlaute, etc.).

### Fehlerbehandlung
Explizite Tests für alle wichtigen Fehlerfälle und Edge Cases.

### Dokumentation
Alle Tests sind mit deutschen Kommentaren dokumentiert, die Zweck und Funktionsweise erklären.

## Erweitern der Tests

### Neue Test-Klasse hinzufügen
```python
class TestNeuesFunktionalität:
    """Tests für neue Funktionalität"""
    
    def test_neue_funktion(self):
        """Test: Beschreibung der neuen Funktion"""
        # Arrange
        test_data = {...}
        
        # Act
        result = neue_funktion(test_data)
        
        # Assert
        assert result == expected_result
```

### Neue Test-Methode hinzufügen
```python
def test_edge_case_neue_situation(self):
    """Test: Neuer Edge Case für bestehende Funktionalität"""
    # Test-Implementierung
    pass
```

## Fehlerbehebung

### Tests schlagen fehl
1. **Abhängigkeiten prüfen**: `pip install -r requirements.txt`
2. **Python-Pfad prüfen**: Tests müssen aus dem Projekt-Root ausgeführt werden
3. **Temporäre Dateien**: Bei persistenten Fehlern `/tmp` leeren

### Neue Tests entwickeln
1. **Test zuerst schreiben** (TDD-Ansatz)
2. **Realistische Testdaten** verwenden
3. **Edge Cases berücksichtigen**
4. **Deutsche Kommentare** für Dokumentation

## Kontinuierliche Integration

Diese Tests sind darauf ausgelegt, in CI/CD-Pipelines integriert zu werden:

```bash
# CI-Pipeline-Kommando
python -m pytest test/test_core_functionality.py --tb=short
```

## Metriken

- **29 Tests** für Kernfunktionalität
- **5 Test-Klassen** für strukturierte Organisation  
- **4 Module** vollständig abgedeckt
- **100% Pass-Rate** bei korrekter Umgebung

---

**Status**: ✅ Produktionstauglich  
**Letzte Aktualisierung**: Juli 2025  
**Framework**: pytest 7.0+