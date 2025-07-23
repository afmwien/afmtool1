#!/usr/bin/env python3
"""
Test für generate_report() Funktion - pytest kompatibel
"""

import sys
import pytest
from pathlib import Path

# AFMTool GUI importieren
sys.path.append(str(Path(__file__).parent.parent / "gui"))
sys.path.append(str(Path(__file__).parent.parent))

def test_generate_report():
    """Test der generate_report Funktion ohne GUI"""
    print("🔍 Teste generate_report() Funktion...")
    
    try:
        from gui.main_window import AFMToolGUI
        
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
            
            assert pdf_path.exists(), "PDF report should be generated"
            
        else:
            pytest.skip("Report-Modul nicht gefunden!")
        
        # GUI-Fenster schließen
        app.root.destroy()
        
    except ImportError as e:
        pytest.skip(f"GUI dependencies not available: {str(e)}")
    except Exception as e:
        pytest.fail(f"Test failed with error: {str(e)}")

def test_basic_imports():
    """Test basic module imports"""
    try:
        import matplotlib
        import reportlab
        assert True, "Basic dependencies available"
    except ImportError as e:
        pytest.fail(f"Basic imports failed: {str(e)}")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])