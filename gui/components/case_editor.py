"""
Case-Editor-Komponente für AFMTool1
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class CaseEditorComponent:
    """Case-Editor-Komponente mit Status-Workflow"""
    
    def __init__(self, parent):
        self.parent = parent
        self.data_service = parent.data_service
        self.status_mapping = parent.status_mapping
        self.case_edit_frame = None
        self.selected_case_index = None
        
        # UI-Elemente
        self.quelle_label = None
        self.fundstellen_label = None
        self.afm_text = None
        self.status_display_frame = None
        self.status_button_frame = None
        self.timestamps_text = None
        
    def create_view(self, container):
        """Case-Edit-View erstellen"""
        self.case_edit_frame = ttk.Frame(container)
        
        # Header
        header_frame = ttk.Frame(self.case_edit_frame)
        header_frame.pack(fill="x", pady=(0, 20))
        
        case_title_label = ttk.Label(header_frame, text="🔧 AFMTool1 - Case Bearbeitung", 
                                     font=("Arial", 16, "bold"))
        case_title_label.pack()
        
        # Case Details Frame
        details_frame = ttk.LabelFrame(self.case_edit_frame, text="📋 Case Details", padding=15)
        details_frame.pack(fill="x", pady=(0, 20))
        
        # Quelle
        ttk.Label(details_frame, text="Quelle:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w", pady=5)
        self.quelle_label = ttk.Label(details_frame, text="", foreground="blue")
        self.quelle_label.grid(row=0, column=1, sticky="w", padx=(10, 0), pady=5)
        
        # Fundstellen
        ttk.Label(details_frame, text="Fundstellen:", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky="w", pady=5)
        self.fundstellen_label = ttk.Label(details_frame, text="", foreground="blue")
        self.fundstellen_label.grid(row=1, column=1, sticky="w", padx=(10, 0), pady=5)
        
        # AFM-String
        ttk.Label(details_frame, text="AFM-String:", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky="nw", pady=5)
        self.afm_text = tk.Text(details_frame, height=4, width=60, wrap="word", state="disabled")
        self.afm_text.grid(row=2, column=1, sticky="w", padx=(10, 0), pady=5)
        
        # Status Workflow Frame
        workflow_frame = ttk.LabelFrame(self.case_edit_frame, text="🔄 Status-Workflow", padding=15)
        workflow_frame.pack(fill="x", pady=(0, 20))
        
        # Status-Anzeige
        self.status_display_frame = ttk.Frame(workflow_frame)
        self.status_display_frame.pack(fill="x", pady=(0, 15))
        
        # Status-Button
        self.status_button_frame = ttk.Frame(workflow_frame)
        self.status_button_frame.pack(fill="x")
        
        # Zeitstempel Frame
        timestamps_frame = ttk.LabelFrame(self.case_edit_frame, text="📅 Zeitstempel", padding=15)
        timestamps_frame.pack(fill="x", pady=(0, 20))
        
        self.timestamps_text = tk.Text(timestamps_frame, height=6, width=80, wrap="word", state="disabled")
        self.timestamps_text.pack(fill="x")
        
        # Action Buttons
        action_frame = ttk.Frame(self.case_edit_frame)
        action_frame.pack(fill="x", pady=(20, 0))
        
        ttk.Button(action_frame, text="🔙 Zurück zum Dashboard", 
                  command=self.parent.show_dashboard_view).pack(side="left")
        ttk.Button(action_frame, text="🔄 Aktualisieren", 
                  command=self.refresh).pack(side="left", padx=(10, 0))
        
        return self.case_edit_frame
    
    def load_case(self, case_index):
        """Case laden und anzeigen"""
        self.selected_case_index = case_index
        cases = self.data_service.get_cases()
        if case_index >= len(cases):
            return
            
        case = cases[case_index]
        
        # Details anzeigen
        self.quelle_label.config(text=case.get("quelle", ""))
        self.fundstellen_label.config(text=case.get("fundstellen", ""))
        
        # AFM-String anzeigen
        self.afm_text.config(state="normal")
        self.afm_text.delete(1.0, tk.END)
        self.afm_text.insert(1.0, case.get("afm_string", ""))
        self.afm_text.config(state="disabled")
        
        # Status-Workflow anzeigen
        self.update_status_workflow(case)
        
        # Zeitstempel anzeigen
        self.update_timestamps_display(case)
    
    def update_status_workflow(self, case):
        """Status-Workflow anzeigen und aktualisieren"""
        current_status = self.data_service.get_case_status(case)
        
        # Status-Display löschen
        for widget in self.status_display_frame.winfo_children():
            widget.destroy()
        for widget in self.status_button_frame.winfo_children():
            widget.destroy()
        
        # Status-Kette anzeigen
        statuses = ["erfassung", "verarbeitung", "validierung", "archivierung"]
        current_index = statuses.index(current_status)
        
        for i, status in enumerate(statuses):
            info = self.status_mapping[status]
            
            if i <= current_index:
                # Erreicht/Aktuell
                label = ttk.Label(self.status_display_frame, 
                                text=f"{info['emoji']} {info['name']}", 
                                foreground=info['color'],
                                font=("Arial", 11, "bold" if i == current_index else "normal"))
            else:
                # Noch nicht erreicht
                label = ttk.Label(self.status_display_frame, 
                                text=f"⚪ {info['name']}", 
                                foreground="gray")
            
            label.pack(side="left", padx=(0, 20))
            
            if i < len(statuses) - 1:
                ttk.Label(self.status_display_frame, text="→").pack(side="left", padx=(0, 20))
        
        # Weiter-Button (falls möglich)
        if current_index < len(statuses) - 1:
            next_status = statuses[current_index + 1]
            next_info = self.status_mapping[next_status]
            
            ttk.Button(self.status_button_frame, 
                      text=f"Weiter zu: {next_info['emoji']} {next_info['name']}", 
                      command=self.advance_status).pack(side="left")
        else:
            ttk.Label(self.status_button_frame, 
                     text="✅ Case abgeschlossen", 
                     foreground="green").pack(side="left")
    
    def update_timestamps_display(self, case):
        """Zeitstempel anzeigen"""
        self.timestamps_text.config(state="normal")
        self.timestamps_text.delete(1.0, tk.END)
        
        timestamps = case.get("zeitstempel", [])
        for ts in timestamps:
            if ":" in ts:
                phase, timestamp = ts.split(":", 1)
                try:
                    dt = datetime.fromisoformat(timestamp)
                    formatted_time = dt.strftime("%Y-%m-%d %H:%M")
                    phase_info = self.status_mapping.get(phase, {"name": phase, "emoji": "•", "color": "#666666"})
                    
                    display_text = f"{phase_info['emoji']} {phase_info['name']}: {formatted_time}\n"
                    self.timestamps_text.insert(tk.END, display_text)
                    
                    # Farbe setzen für den letzten eingefügten Text
                    line_start = f"{self.timestamps_text.index(tk.END)} -1 line linestart"
                    line_end = f"{self.timestamps_text.index(tk.END)} -1 line lineend"
                    self.timestamps_text.tag_add(f"color_{phase}", line_start, line_end)
                    self.timestamps_text.tag_configure(f"color_{phase}", foreground=phase_info['color'])
                except:
                    self.timestamps_text.insert(tk.END, f"• {ts}\n")
        
        self.timestamps_text.config(state="disabled")
    
    def advance_status(self):
        """Status weiterschalten"""
        if self.selected_case_index is not None:
            success = self.data_service.advance_case_status(self.selected_case_index)
            if success:
                self.refresh()
                from utils.logger import log_action
                log_action("GUI_ACTION", f"Status gewechselt für Case {self.selected_case_index}")
            else:
                messagebox.showinfo("Status", "Case ist bereits abgeschlossen.")
    
    def refresh(self):
        """Case-Ansicht aktualisieren"""
        if self.selected_case_index is not None:
            self.load_case(self.selected_case_index)
    
    def show(self, case_index):
        """Case-Editor anzeigen"""
        self.case_edit_frame.pack(fill="both", expand=True)
        self.load_case(case_index)
    
    def hide(self):
        """Case-Editor ausblenden"""
        self.case_edit_frame.pack_forget()
