#!/usr/bin/env python3
"""
Test für generate_report() Funktion
"""

import sys
from pathlib import Path

# AFMTool GUI importieren
sys.path.append(str(Path(__file__).parent / "gui"))
sys.path.append(str(Path(__file__).parent))
from gui.main_window import AFMToolGUI

def test_generate_report():
    """Test der generate_report Funktion ohne GUI"""
    print("🔍 Teste generate_report() Funktion...")
    
    try:
        # GUI-Instanz erstellen (ohne mainloop)
        app = AFMToolGUI()
        
        # Report-Pfad prüfen
        report_module_path = app.cases_file.parent / "report" / "report.py"
        print(f"📁 Report-Modul-Pfad: {report_module_path}")
        print(f"✅ Report-Modul existiert: {report_module_path.exists()}")
        
        if report_module_path.exists():
            # Import testen
            import importlib.util
            spec = importlib.util.spec_from_file_location("report", report_module_path)
            report_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(report_module)
            print("✅ Report-Modul erfolgreich importiert")
            
            # AFMReporter Klasse testen
            reporter = report_module.AFMReporter()
            print("✅ AFMReporter Instanz erstellt")
            
            # PDF generieren testen
            pdf_path = reporter.generate_pdf_report()
            print(f"✅ PDF-Report generiert: {pdf_path}")
            print(f"📄 PDF existiert: {pdf_path.exists()}")
            
        else:
            print("❌ Report-Modul nicht gefunden!")
        
        # GUI-Fenster schließen
        app.root.destroy()
        
    except Exception as e:
        print(f"❌ Fehler beim Test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_generate_report()
