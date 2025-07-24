#!/usr/bin/env python3
"""
AFMTool1 - Report Dashboard Test
Zeigt nur das Main Window der GUI für Dashboard-Tests
"""

import sys
import tkinter as tk
from tkinter import ttk
from pathlib import Path

# GUI Module importieren
try:
    from gui.main_window import AFMToolGUI
    GUI_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ GUI Module nicht verfügbar: {e}")
    GUI_AVAILABLE = False

class ReportDashboard:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AFMTool1 - Report Dashboard")
        self.root.geometry("800x600")
        
        # Main Frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="AFMTool1 Report Dashboard", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Buttons Frame
        buttons_frame = ttk.LabelFrame(main_frame, text="Report Funktionen", padding="10")
        buttons_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Test Buttons
        ttk.Button(buttons_frame, text="📊 PDF Matrix Report", 
                  command=self.test_pdf_report, width=25).grid(row=0, column=0, padx=5, pady=5)
        
        ttk.Button(buttons_frame, text="📋 TXT Case Report", 
                  command=self.test_txt_report, width=25).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Button(buttons_frame, text="🎯 GUI Main Window", 
                  command=self.open_main_gui, width=25).grid(row=1, column=0, padx=5, pady=5)
        
        ttk.Button(buttons_frame, text="📁 Projekt Struktur", 
                  command=self.test_structure, width=25).grid(row=1, column=1, padx=5, pady=5)
        
        # Status Frame
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="10")
        status_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        
        # Text widget für Status
        self.status_text = tk.Text(status_frame, height=15, width=80)
        scrollbar = ttk.Scrollbar(status_frame, orient="vertical", command=self.status_text.yview)
        self.status_text.configure(yscrollcommand=scrollbar.set)
        
        self.status_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        status_frame.columnconfigure(0, weight=1)
        status_frame.rowconfigure(0, weight=1)
        
        # Initial Status
        self.log("🚀 AFMTool1 Report Dashboard gestartet")
        self.log(f"📂 Arbeitsverzeichnis: {Path.cwd()}")
        if GUI_AVAILABLE:
            self.log("✅ GUI Module verfügbar")
        else:
            self.log("❌ GUI Module nicht verfügbar")
    
    def log(self, message):
        """Nachricht im Status-Bereich anzeigen"""
        self.status_text.insert(tk.END, f"{message}\n")
        self.status_text.see(tk.END)
        self.root.update()
    
    def test_pdf_report(self):
        """PDF Report testen"""
        self.log("📊 Teste PDF Matrix Report...")
        try:
            from data.report.report import AFMReporter
            reporter = AFMReporter()
            
            # Datenbank Übersicht
            overview = reporter.get_database_overview()
            self.log(f"   Datenbanken gefunden: {len(overview)}")
            
            # PDF generieren
            pdf_path = reporter.generate_pdf_report()
            self.log(f"✅ PDF Report erstellt: {pdf_path}")
            
        except Exception as e:
            self.log(f"❌ Fehler bei PDF Report: {e}")
    
    def test_txt_report(self):
        """TXT Report testen"""
        self.log("📋 Teste TXT Case Report...")
        try:
            from data.report.case_report import CaseReporter
            reporter = CaseReporter()
            
            # Cases laden
            cases = reporter.load_cases()
            self.log(f"   Cases geladen: {len(cases)}")
            
            # TXT Report generieren
            txt_path = reporter.generate_case_list()
            if txt_path:
                self.log(f"✅ TXT Report erstellt: {txt_path}")
            else:
                self.log("❌ TXT Report konnte nicht erstellt werden")
                
        except Exception as e:
            self.log(f"❌ Fehler bei TXT Report: {e}")
    
    def open_main_gui(self):
        """Haupt-GUI öffnen"""
        self.log("🎯 Öffne Haupt-GUI...")
        if not GUI_AVAILABLE:
            self.log("❌ GUI Module nicht verfügbar")
            return
            
        try:
            # Neues Fenster für Haupt-GUI
            gui_window = tk.Toplevel(self.root)
            gui_window.title("AFMTool1 - Haupt GUI")
            gui_window.geometry("900x700")
            
            # Haupt-GUI initialisieren (ohne mainloop)
            app = AFMToolGUI()
            # GUI in das neue Fenster einbetten
            app.root = gui_window
            app.setup_gui()
            
            self.log("✅ Haupt-GUI geöffnet")
            
        except Exception as e:
            self.log(f"❌ Fehler beim Öffnen der Haupt-GUI: {e}")
    
    def test_structure(self):
        """Projekt-Struktur anzeigen"""
        self.log("📁 Analysiere Projekt-Struktur...")
        try:
            project_root = Path.cwd()
            
            # Wichtige Verzeichnisse
            directories = ["gui", "utils", "data", "test", ".github"]
            for dir_name in directories:
                dir_path = project_root / dir_name
                if dir_path.exists():
                    files = list(dir_path.glob("*.py"))
                    self.log(f"   📂 {dir_name}/: {len(files)} Python-Dateien")
                else:
                    self.log(f"   ❌ {dir_name}/: Nicht gefunden")
            
            # Haupt-Dateien
            main_files = ["main.py", "main_gui.py", "requirements.txt", "README.md"]
            for file_name in main_files:
                file_path = project_root / file_name
                if file_path.exists():
                    size = file_path.stat().st_size
                    self.log(f"   📄 {file_name}: {size} Bytes")
                else:
                    self.log(f"   ❌ {file_name}: Nicht gefunden")
            
            self.log("✅ Struktur-Analyse abgeschlossen")
            
        except Exception as e:
            self.log(f"❌ Fehler bei Struktur-Analyse: {e}")
    
    def run(self):
        """Dashboard starten"""
        self.root.mainloop()

def main():
    """Dashboard-Anwendung starten"""
    print("🚀 AFMTool1 Report Dashboard wird gestartet...")
    
    try:
        dashboard = ReportDashboard()
        dashboard.run()
    except Exception as e:
        print(f"❌ Fehler beim Starten des Dashboards: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
