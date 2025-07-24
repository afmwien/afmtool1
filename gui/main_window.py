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
from .components import DashboardComponent, CaseEditorComponent, ImageViewerComponent
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
        # HINWEIS: Status "NEU" hat zwei Bedeutungen:
        # 1. Importierte Cases: Status "erfassung" = muss bearbeitet werden
        # 2. Händisch angelegte Cases: Status "erfassung" = Felder sind leer/neu
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
        """GUI-Layout erstellen - Tab-basiert für Web-Portierung"""
        # Tab-Navigation erstellen
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Container für Views
        self.dashboard_container = ttk.Frame(self.notebook)
        self.case_edit_container = ttk.Frame(self.notebook)
        self.image_viewer_container = ttk.Frame(self.notebook)
        
        # Komponenten erstellen
        self.dashboard = DashboardComponent(self)
        self.case_editor = CaseEditorComponent(self)
        self.image_viewer = ImageViewerComponent(self)
        
        # Views erstellen und in Container packen
        self.dashboard_frame = self.dashboard.create_view(self.dashboard_container)
        self.dashboard_frame.pack(fill="both", expand=True)
        
        self.case_edit_frame = self.case_editor.create_view(self.case_edit_container)
        self.case_edit_frame.pack(fill="both", expand=True)
        
        self.image_viewer_frame = self.image_viewer.create_view(self.image_viewer_container)
        self.image_viewer_frame.pack(fill="both", expand=True)
        
        # Tabs hinzufügen
        self.notebook.add(self.dashboard_container, text="📊 Dashboard")
        self.notebook.add(self.case_edit_container, text="✏️ Case Editor")
        self.notebook.add(self.image_viewer_container, text="🖼️ Bildvergleich")
        
        # Tab-Wechsel Event
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        
        # Initial Dashboard anzeigen und Daten laden
        self.notebook.select(0)
        self.dashboard.refresh()
    
    def show_dashboard_view(self):
        """Dashboard-Ansicht anzeigen mit Warnung bei ungespeicherten Änderungen"""
        # Prüfe ob Case-Editor ungespeicherte Änderungen hat
        if hasattr(self, 'case_editor') and self.case_editor.has_unsaved_changes():
            from tkinter import messagebox
            
            result = messagebox.askyesnocancel(
                "Ungespeicherte Änderungen",
                "Sie haben ungespeicherte Änderungen im Case-Editor.\n\n"
                "Möchten Sie die Änderungen speichern?\n\n"
                "Ja = Speichern und zurück\n"
                "Nein = Verwerfen und zurück\n"
                "Abbrechen = Beim Editor bleiben"
            )
            
            if result is None:  # Abbrechen
                return
            elif result:  # Ja - speichern
                self.case_editor.save_changes()
            # Nein = einfach weitermachen ohne speichern
        
        # Automatische Bereinigung leerer Cases
        self.data_service.cleanup_empty_cases()
        
        self.notebook.select(0)
        self.dashboard.refresh()
        self.current_view = "dashboard"
    
    def show_case_edit_view(self, case_index):
        """Case-Bearbeitung-Ansicht anzeigen"""
        self.notebook.select(1)
        self.case_editor.show(case_index)
        self.current_view = "case_edit"
    
    def show_image_viewer_with_case(self, case_data):
        """Image Viewer mit Case-Daten anzeigen"""
        self.notebook.select(2)  # Tab 2 = Image Viewer
        self.image_viewer.load_case_data(case_data)
    
    def show_case_editor_view(self):
        """Case Editor anzeigen"""
        self.notebook.select(1)  # Tab 1 = Case Editor
    
    def on_tab_changed(self, event):
        """Tab-Wechsel Event Handler"""
        selected_tab = self.notebook.index(self.notebook.select())
        if selected_tab == 0:
            self.current_view = "dashboard"
            self.dashboard.refresh()
        elif selected_tab == 1:
            self.current_view = "case_edit"
        elif selected_tab == 2:
            self.current_view = "image_viewer"
    
    def edit_case(self, case_index):
        """Case zur Bearbeitung öffnen"""
        self.show_case_edit_view(case_index)
        log_action("GUI_ACTION", f"Case {case_index} zur Bearbeitung geöffnet")
    
    def edit_new_case(self, case_index):
        """Neuen Case zur Bearbeitung öffnen - automatisch im Edit-Modus"""
        self.show_case_edit_view(case_index)
        # Case-Editor in Edit-Modus setzen und Tracking aktivieren
        self.case_editor.edit_mode = True
        self.case_editor.is_editing = True
        self.case_editor.original_quelle = self.case_editor.quelle_entry.get().strip() if self.case_editor.quelle_entry else ""
        self.case_editor.original_fundstellen = self.case_editor.fundstellen_entry.get().strip() if self.case_editor.fundstellen_entry else ""
        self.case_editor.update_ui_mode()
        log_action("GUI_ACTION", f"Neuer Case {case_index} im Edit-Modus geöffnet")
    
    def generate_report(self):
        """PDF-Report generieren"""
        try:
            # Import des Report-Moduls mit absolutem Pfad
            report_module_path = self.cases_file.parent / "report" / "report.py"
            
            if report_module_path.exists():
                import importlib.util
                spec = importlib.util.spec_from_file_location("report", report_module_path)
                report_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(report_module)
                
                # Reporter erstellen und PDF generieren
                reporter = report_module.AFMReporter()
                pdf_path = reporter.generate_pdf_report()
                
                messagebox.showinfo("Report", f"PDF-Report erfolgreich generiert!\n\nDatei: {pdf_path.name}")
                log_action("GUI_ACTION", f"PDF-Report generiert: {pdf_path}")
            else:
                messagebox.showerror("Fehler", "Report-Modul nicht gefunden!")
                log_action("GUI_ERROR", "Report-Modul nicht gefunden")

        except Exception as e:
            messagebox.showerror("Report Fehler", f"Fehler beim Generieren des Reports:\n{str(e)}")
            log_action("GUI_ERROR", f"Report-Fehler: {str(e)}")
    
    def quit_app(self):
        """Anwendung beenden mit Session-Cleanup"""
        try:
            # Session-Daten synchronisieren und bereinigen
            if hasattr(self, 'data_service'):
                print("🔄 [QUIT] Starte Session-Cleanup...")
                self.data_service.sync_and_shutdown()
            
            log_action("GUI_STOP", "AFMTool GUI beendet")
            self.root.quit()
            self.root.destroy()
            
        except Exception as e:
            print(f"⚠️ [QUIT] Fehler beim Beenden: {e}")
            # Trotzdem beenden, auch wenn Cleanup fehlschlägt
            self.root.quit()
            self.root.destroy()
    
    def show_message(self, title, message):
        """Zeigt Message-Dialog für Benutzer-Feedback"""
        try:
            messagebox.showinfo(title, message)
        except Exception as e:
            print(f"⚠️ [MESSAGE] Dialog-Fehler: {e}")
            print(f"📢 [MESSAGE] {title}: {message}")
    
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
