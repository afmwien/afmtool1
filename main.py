#!/usr/bin/env python3
"""
AFMTool1 - Minimales Python Tool
"""

from utils.database import load_database
from utils.logger import log_action

def main():
    """Haupt-Einstiegspunkt"""
    print("AFMTool1 gestartet")
    log_action("START", "AFMTool1 gestartet")
    
    while True:
        print("\n--- AFMTool1 ---")
        print("1. Case hinzufügen")
        print("2. Cases anzeigen")
        print("3. Beenden")
        
        choice = input("Wahl: ").strip()
        
        if choice == "1":
            print("❌ CLI Case-Erstellung entfernt - verwende GUI!")
            
        elif choice == "2":
            data = load_database()
            print(f"\nGefunden: {len(data['cases'])} Cases")
            for i, case in enumerate(data['cases'], 1):
                print(f"{i}. Quelle: {case['quelle']}, Fundstellen: {case['fundstellen']}")
                
        elif choice == "3":
            log_action("STOP", "AFMTool1 beendet")
            print("Auf Wiedersehen!")
            break
            
        else:
            print("Ungültige Eingabe!")

if __name__ == "__main__":
    main()
