"""
Dashboard-Komponente für AFMTool1
"""
import tkinter as tk
from tkinter import ttk
from .dialogs import CaseInputDialog

class DashboardComponent:
    """Dashboard-Komponente mit Case-Tabelle und Buttons"""
    
    def __init__(self, parent):
        self.parent = parent
        self.data_service = parent.data_service
        self.status_mapping = parent.status_mapping
        self.dashboard_frame = None
        self.tree = None
        
    def create_view(self, container):
        """Dashboard-View erstellen"""
        self.dashboard_frame = ttk.Frame(container)
        
        # Header
        header_frame = ttk.Frame(self.dashboard_frame)
        header_frame.pack(fill="x", pady=(0, 20))
        
        title_label = ttk.Label(header_frame, text="🔧 AFMTool1 - Case Management", 
                               font=("Arial", 16, "bold"))
        title_label.pack()
        
        # Case-Tabelle mit Treeview
        self.create_case_table()
        
        # Buttons
        button_frame = ttk.Frame(self.dashboard_frame)
        button_frame.pack(fill="x", pady=(20, 0))
        
        ttk.Button(button_frame, text="📝 Neuer Case", 
                  command=self.new_case).pack(side="left", padx=(0, 10))
        ttk.Button(button_frame, text="🔄 Aktualisieren", 
                  command=self.refresh).pack(side="left", padx=(0, 10))
        ttk.Button(button_frame, text="📊 Report", 
                  command=self.parent.generate_report).pack(side="right", padx=(10, 0))
        ttk.Button(button_frame, text="❌ Beenden", 
                  command=self.parent.quit_app).pack(side="right")
        
        return self.dashboard_frame
    
    def create_case_table(self):
        """Case-Tabelle mit Treeview erstellen"""
        # Frame für Tabelle
        table_frame = ttk.Frame(self.dashboard_frame)
        table_frame.pack(fill="both", expand=True)
        
        # Treeview
        columns = ("quelle", "fundstellen", "status", "aktion")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        # Spalten-Header
        self.tree.heading("quelle", text="Quelle")
        self.tree.heading("fundstellen", text="Fundstellen")
        self.tree.heading("status", text="Status")
        self.tree.heading("aktion", text="Aktion")
        
        # Spalten-Breite
        self.tree.column("quelle", width=250)
        self.tree.column("fundstellen", width=300)
        self.tree.column("status", width=150)
        self.tree.column("aktion", width=120)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Doppelklick-Event für Bearbeitung
        self.tree.bind("<Double-1>", self.on_case_double_click)
    
    def populate_table(self):
        """Tabelle mit Cases füllen"""
        # Alte Einträge löschen
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Cases laden
        cases = self.data_service.get_cases()
        
        for i, case in enumerate(cases):
            status = self.data_service.get_case_status(case)
            status_info = self.status_mapping[status]
            
            status_display = f"{status_info['emoji']} {status_info['name']}"
            
            self.tree.insert("", "end", values=(
                case.get("quelle", ""),
                case.get("fundstellen", ""),
                status_display,
                "→ Bearbeiten"
            ), tags=(str(i),))
    
    def on_case_double_click(self, event):
        """Case-Doppelklick - Bearbeitung öffnen"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            case_index = int(item['tags'][0])
            self.parent.edit_case(case_index)
    
    def new_case(self):
        """Neuen Case erstellen"""
        dialog = CaseInputDialog(self.parent.root)
        if dialog.result:
            quelle, fundstellen = dialog.result
            case = self.data_service.create_case(quelle, fundstellen)
            from utils.logger import log_action
            from tkinter import messagebox
            messagebox.showinfo("Erfolg", f"Neuer Case erstellt:\n{quelle}")
            log_action("GUI_ACTION", f"Neuer Case erstellt: {quelle}")
            self.refresh()
    
    def refresh(self):
        """Dashboard aktualisieren"""
        self.populate_table()
    
    def show(self):
        """Dashboard anzeigen"""
        self.dashboard_frame.pack(fill="both", expand=True)
        self.refresh()
    
    def hide(self):
        """Dashboard ausblenden"""
        self.dashboard_frame.pack_forget()
