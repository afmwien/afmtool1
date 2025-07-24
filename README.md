# AFMTool1

**Pure AFM-String System** - Minimales Python-Tool für AFM-Workflow-Automation.

## 🚀 Quick Start

### Installation
```bash
# Dependencies installieren
pip install -r requirements.txt

# GUI starten
python main_gui.py

# Terminal-Version
python main.py
```

### Features
- **Pure AFM-String Workflow**: Base64-verschlüsselte AFM-Strings als Single Source of Truth
- **GUI-Interface**: Tkinter-basierte Benutzeroberfläche mit Case-Management
- **Report-System**: PDF-Matrix-View und TXT-Fallnummer-Gruppierung
- **Session-basiert**: Automatische Export/Import-Workflows
- **GitHub Actions**: CI/CD mit Quality-Tests

## 📁 Struktur
```
afmtool/
├── gui/              # Benutzeroberfläche
├── utils/            # AFM-Core & Helper
├── data/             # Cases & Reports
├── test/             # Test-Suite
└── .github/          # CI/CD Workflows
```

## 🔧 Entwicklung
```bash
# Tests ausführen
python test_quality.py

# Quality-Check
pytest test_quality.py -v
```

## GitHub
Repository: `afmwien/afmtool1`
