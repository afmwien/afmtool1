#!/usr/bin/env python3
"""
AFMTool1 - GUI Launcher
Startet die grafische Benutzeroberfläche für AFMTool
"""

import sys
from pathlib import Path

# GUI Module importieren
from gui.main_window import AFMToolGUI

def main():
    """GUI-Anwendung starten"""
    print("🚀 AFMTool1 GUI wird gestartet...")
    
    try:
        app = AFMToolGUI()
        app.run()
    except Exception as e:
        print(f"❌ Fehler beim Starten der GUI: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
