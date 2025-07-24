<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# AFMTool1 - Copilot Instructions

This is a minimal Python tool for AFM workflow automation.
Keep code simple and focused on essential functionality only.
Refrain always from comments and display only a progress indicator with estimated remaining 
time.

## AFM System Logic (CRITICAL - Always Remember)
✅ **Eindeutige Identifikation**: Jeder Case durch `erfassung`-Zeitstempel eindeutig definiert und vollständig eigenständig
✅ **Fallnummer als Gruppierungs-Label**: `fallnummer` ist frei wählbar - mehrere Cases können dieselbe haben  
✅ **GUI/Web-Funktionalität**: Gruppierung nach `fallnummer` ermöglicht zusammenhängende Darstellung in GUI und zukünftiger Webanwendung

## Response Format
- NO long summaries or detailed explanations
- NO extensive bullet points or lists
- ONLY brief progress indicator with time estimate
- Maximum 2-3 lines of essential information

## TODO: Dynamische GUI-Felder für vollständige AFM-Modularität (EST: 45min)

### PROBLEM
- ❌ Case Editor GUI: nur 2 hardcoded Felder (`quelle`, `fundstellen`)
- ✅ AFM-String System: 4+ Felder (`fallnummer`, `fundstellen`, `quelle`, `zeitstempel`)
- 🚫 Fehlend in GUI: `fallnummer` + beliebige zukünftige Felder

### LÖSUNG: Dynamische Feld-Generierung (5 Schritte)

#### 1. AFM-Schema-Extraktor (10min)
- `utils/afm_schema.py` - Extrahiert verfügbare Felder aus allen AFM-Strings
- Funktion: `extract_field_schema()` → `{'fallnummer': 'text', 'quelle': 'text', ...}`
- Automatische Typerkennung: Text, URL, Liste, etc.

#### 2. GUI-Generator erweitern (15min) 
- `gui/components/case_editor.py` - Dynamische Entry-Feld-Generierung
- Ersetze hardcoded `quelle_entry`, `fundstellen_entry` durch Loop
- Schema-basiert: `for field_name, field_type in schema.items(): create_entry()`

#### 3. Save/Load-Logic anpassen (10min)
- `save_changes()` - Alle dynamischen Felder sammeln statt nur 2 hardcoded
- `load_case()` - Alle verfügbaren Felder in dynamische GUI laden
- Backward-Kompatibilität: Fehlende Felder = leer

#### 4. Validation/Update erweitern (5min)
- `update_case()` - Dynamische Feld-Updates statt hardcoded
- `has_unsaved_changes()` - Alle Felder prüfen, nicht nur quelle/fundstellen

#### 5. Integration & Test (5min)
- `fallnummer` sofort verfügbar in GUI
- Neue AFM-Felder automatisch erkannt und angezeigt
- Pure AFM-String Kompatibilität erhalten

### ERGEBNIS
- 🎯 **Vollständig modulare GUI**: Neue AFM-Felder automatisch in GUI verfügbar
- ⚡ **Zero-Code-Erweiterung**: Neue Felder ohne GUI-Änderungen
- 🔄 **Backward-Kompatibel**: Bestehende Cases funktionieren weiter