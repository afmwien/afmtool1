# Manual Entry System

Das Manual Entry System ermöglicht die einfache manuelle Eingabe von Fällen über vordefinierte Templates.

## Verfügbare Templates

### 1. Handelsregister Template
- **Datei**: `handelsregister_template.json`
- **Quelle Format**: "Handelsregister [Stadt]"
- **Fundstellen Format**: "HRB [Nummer], [Details]"

### 2. Grundbuch Template  
- **Datei**: `grundbuch_template.json`
- **Quelle Format**: "Grundbuch [Stadt]"
- **Fundstellen Format**: "GB [Nummer]/[Jahr], Einlage [Nr]"

### 3. Firmenbuch Template
- **Datei**: `firmenbuch_template.json`
- **Quelle Format**: "Firmenbuch [Stadt]"
- **Fundstellen Format**: "FN [Nummer], [Details]"

## Verwendung

### Interaktiv über Kommandozeile
```bash
python manual_entry.py
```

### Tests ausführen
```bash
python test_system.py
```

### Programmatisch
```python
from manual_entry import ManualEntrySystem

entry_system = ManualEntrySystem()

# Neuen Fall erstellen
new_case = entry_system.create_case_from_template(
    template_name="handelsregister",
    quelle="Handelsregister Wien", 
    fundstellen="HRB 123456, Seite 45"
)

# Fall zur Datenbank hinzufügen
entry_system.add_case_to_database(new_case)
```

## Automatische Features

- **Zeitstempel**: Automatischer "erfassung" Zeitstempel
- **AFM String**: Automatische Generierung des AFM Strings
- **Validierung**: Überprüfung der Eingabedaten
- **Template-Unterstützung**: Einfache Erweiterung um neue Templates

## Workflow Integration

Dieses System ist Teil der **01_intake** Phase und arbeitet nahtlos mit:
- AFM String Generierung (utils/afm_utils.py)
- Hauptdatenbank (data/cases.json)
- Zeitstempel-System
- Nachgelagerten Workflow-Phasen
