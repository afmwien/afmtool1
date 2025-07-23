#!/usr/bin/env python3
"""
AFMTool1 - Minimales Python Tool
"""

from utils.database import add_person, load_database
from utils.logger import log_action

def main():
    """Haupt-Einstiegspunkt"""
    print("AFMTool1 gestartet")
    log_action("START", "AFMTool1 gestartet")
    
    while True:
        print("\n--- AFMTool1 ---")
        print("1. Person hinzufügen")
        print("2. Personen anzeigen")
        print("3. Beenden")
        
        choice = input("Wahl: ").strip()
        
        if choice == "1":
            quelle = input("Quelle: ").strip()
            fundstellen = input("Fundstellen: ").strip()
            add_person(quelle, fundstellen)
            log_action("ADD_PERSON", f"Quelle: {quelle}, Fundstellen: {fundstellen}")
            print("Person hinzugefügt!")
            
        elif choice == "2":
            data = load_database()
            print(f"\nGefunden: {len(data['persones'])} Personen")
            for i, person in enumerate(data['persones'], 1):
                print(f"{i}. Quelle: {person['quelle']}, Fundstellen: {person['fundstellen']}")
                
        elif choice == "3":
            log_action("STOP", "AFMTool1 beendet")
            print("Auf Wiedersehen!")
            break
            
        else:
            print("Ungültige Eingabe!")

if __name__ == "__main__":
    main()
