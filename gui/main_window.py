#!/usr/bin/env python3
"""
AFMTool - GUI Hauptfenster
Grafische Benutzeroberfläche für Case Management
Web-kompatible Architektur mit Desktop tkinter Frontend
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
from pathlib import Path

# Komponenten importieren
from .components import DashboardComponent, CaseEditorComponent
from .services import DataService

# Utils importieren
sys.path.append(str(Path(__file__).parent.parent))
from utils.logger import log_action

class AFMToolGUI:
    """Hauptfenster der AFMTool GUI - Web-kompatible Architektur"""
    
    def __init__(self):
        # GUI Framework (tkinter für Desktop, später Flask für Web)
        self.root = tk.Tk()
        self.root.title("AFMTool1 - GUI Interface")
        self.root.geometry("1200x800")
        
        # Data Service Layer (web-kompatibel)
        self.cases_file = Path(__file__).parent.parent / "data" / "cases.json"
        self.data_service = DataService(self.cases_file)
        
        # View State
        self.current_view = "dashboard"
        
        # Status-Mapping (erfassung → NEU, etc.)
        self.status_mapping = {
            "erfassung": {"name": "NEU", "emoji": "🔴", "color": "#FF0000", "next": "verarbeitung"},
            "verarbeitung": {"name": "Bearbeitung", "emoji": "🟡", "color": "#FFD700", "next": "validierung"},
            "validierung": {"name": "Freigegeben", "emoji": "🟢", "color": "#00AA00", "next": "archivierung"},
            "archivierung": {"name": "Abgeschlossen", "emoji": "⚫", "color": "#333333", "next": None}
        }
        
        # GUI-Setup
        self.setup_gui()
        
        # Logging
        log_action("GUI_START", "AFMTool GUI gestartet")
    
    def setup_gui(self):
        """GUI-Layout erstellen - Modular für Web-Portierung"""
        # Container für View-Switching
        self.container = ttk.Frame(self.root)
        self.container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Komponenten erstellen
        self.dashboard = DashboardComponent(self)
        self.case_editor = CaseEditorComponent(self)
        
        # Views erstellen
        self.dashboard_frame = self.dashboard.create_view(self.container)
        self.case_edit_frame = self.case_editor.create_view(self.container)
        
        # Initial Dashboard anzeigen
        self.show_dashboard_view()
    
    def show_dashboard_view(self):
        """Dashboard-Ansicht anzeigen"""
        self.case_editor.hide()
        self.dashboard.show()
        self.current_view = "dashboard"
    
    def show_case_edit_view(self, case_index):
        """Case-Bearbeitung-Ansicht anzeigen"""
        self.dashboard.hide()
        self.case_editor.show(case_index)
        self.current_view = "case_edit"
    
    def edit_case(self, case_index):
        """Case zur Bearbeitung öffnen"""
        self.show_case_edit_view(case_index)
        log_action("GUI_ACTION", f"Case {case_index} zur Bearbeitung geöffnet")
    
    def generate_report(self):
        """PDF-Report generieren"""
        try:
            # Import des Report-Moduls
            report_path = self.cases_file.parent / "report"
            if str(report_path) not in sys.path:
                sys.path.append(str(report_path))
            
            from report import AFMReporter
            
            # Reporter erstellen und PDF generieren
            reporter = AFMReporter()
            pdf_path = reporter.generate_pdf_report()
            
            messagebox.showinfo("Report", f"PDF-Report erfolgreich generiert!\n\nDatei: {pdf_path.name}")
            log_action("GUI_ACTION", f"PDF-Report generiert: {pdf_path}")
            
        except Exception as e:
            messagebox.showerror("Report Fehler", f"Fehler beim Generieren des Reports:\n{str(e)}")
            log_action("GUI_ERROR", f"Report-Fehler: {str(e)}")
    
    def quit_app(self):
        """Anwendung beenden"""
        log_action("GUI_STOP", "AFMTool GUI beendet")
        self.root.quit()
        self.root.destroy()
    
    def run(self):
        """GUI starten"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.quit_app()

def main():
    """GUI-Launcher"""
    app = AFMToolGUI()
    app.run()

if __name__ == "__main__":
    main()
