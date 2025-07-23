#!/usr/bin/env python3
"""
Test-Runner für AFMTool1 Kernfunktionalität
==========================================

Dieses Skript führt die umfassenden Tests für die AFMTool1 Kernfunktionalität aus
und stellt sicher, dass alle grundlegenden Module ordnungsgemäß funktionieren.

Verwendung:
    python run_core_tests.py              # Führt alle Kerntests aus
    python run_core_tests.py --verbose    # Ausführliche Ausgabe
    python run_core_tests.py --coverage   # Mit Coverage-Report
"""

import sys
import subprocess
from pathlib import Path

def run_tests(verbose=False, coverage=False):
    """
    Führt die Kerntests aus mit optionaler Ausführlichkeit und Coverage
    
    Args:
        verbose (bool): Ausführliche Ausgabe der Tests
        coverage (bool): Coverage-Report generieren
    """
    
    # Zum Projekt-Root wechseln
    project_root = Path(__file__).parent
    
    print("🧪 AFMTool1 Kernfunktionalität Tests")
    print("=" * 50)
    
    # Basis-Kommando zusammenstellen
    cmd = [sys.executable, "-m", "pytest", "test/test_core_functionality.py"]
    
    if verbose:
        cmd.append("-v")
        cmd.append("--tb=short")
    
    if coverage:
        cmd.extend(["--cov=utils", "--cov-report=term-missing"])
    
    # Tests ausführen
    try:
        print(f"🔄 Führe aus: {' '.join(cmd)}")
        result = subprocess.run(cmd, cwd=project_root, capture_output=True, text=True)
        
        # Ausgabe anzeigen
        if result.stdout:
            print("\n📊 Test-Ergebnisse:")
            print("-" * 30)
            print(result.stdout)
        
        if result.stderr:
            print("\n⚠️ Warnungen/Fehler:")
            print("-" * 30) 
            print(result.stderr)
        
        # Exit-Code prüfen
        if result.returncode == 0:
            print("\n✅ Alle Tests erfolgreich!")
            return True
        else:
            print(f"\n❌ Tests fehlgeschlagen (Exit Code: {result.returncode})")
            return False
            
    except Exception as e:
        print(f"\n💥 Fehler beim Ausführen der Tests: {str(e)}")
        return False

def print_test_overview():
    """Zeigt eine Übersicht der verfügbaren Tests"""
    print("\n📋 Test-Übersicht - AFMTool1 Kernfunktionalität:")
    print("-" * 50)
    print("🗃️  Database-Operationen:")
    print("   • load_database() - Datenbank laden")
    print("   • save_database() - Datenbank speichern") 
    print("   • add_case_with_fields() - Cases hinzufügen")
    print("   • get_cases_count() - Anzahl Cases abrufen")
    print("   • get_last_filled_cases() - Letzte Cases abrufen")
    print("   • get_latest_case_info() - Neueste Case-Info")
    
    print("\n🔧 AFM-String-Utilities:")
    print("   • generate_afm_string_for_case() - AFM-String generieren")
    print("   • update_case_afm_string() - AFM-String aktualisieren")
    print("   • add_timestamp_to_case() - Zeitstempel hinzufügen")
    print("   • get_timestamps_from_case() - Zeitstempel extrahieren")
    print("   • validate_afm_strings() - AFM-Strings validieren")
    
    print("\n📝 Logger-Funktionalität:")
    print("   • log_action() - Aktionen protokollieren")
    print("   • get_log_entries() - Log-Einträge abrufen")
    
    print("\n✅ Eingabevalidierung & Edge Cases:")
    print("   • Sonderzeichen (Umlaute, Symbole)")
    print("   • Sehr lange Strings") 
    print("   • Leerzeichen und leere Werte")
    print("   • Fehlerhaftes JSON")
    print("   • Verschachtelte Daten")
    print("   • Gemischte Datentypen")
    print("   • Ungültige Datenbankstrukturen")

def main():
    """Hauptfunktion - verarbeitet Kommandozeilenargumente"""
    
    # Kommandozeilenargumente verarbeiten
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    coverage = "--coverage" in sys.argv or "--cov" in sys.argv
    help_requested = "--help" in sys.argv or "-h" in sys.argv
    
    if help_requested:
        print(__doc__)
        print_test_overview()
        return
    
    # Übersicht anzeigen wenn keine speziellen Optionen gewählt
    if not (verbose or coverage):
        print_test_overview()
        print()
    
    # Tests ausführen
    success = run_tests(verbose=verbose, coverage=coverage)
    
    if success:
        print("\n🎉 AFMTool1 Kernfunktionalität vollständig getestet!")
        print("🚀 Alle Module arbeiten ordnungsgemäß.")
        sys.exit(0)
    else:
        print("\n🔧 Bitte Fehler beheben und Tests erneut ausführen.")
        sys.exit(1)

if __name__ == "__main__":
    main()