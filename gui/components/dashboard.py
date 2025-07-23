"""
Dashboard-Komponente für AFMTool1
"""
import tkinter as tk
from tkinter import ttk

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
        ttk.Button(button_frame, text=" Report", 
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
        columns = ("quelle", "fundstellen", "status", "links", "aktion", "bildvergleich")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        # Spalten-Header
        self.tree.heading("quelle", text="Quelle")
        self.tree.heading("fundstellen", text="Fundstellen")
        self.tree.heading("status", text="Status")
        self.tree.heading("links", text="Links")
        self.tree.heading("aktion", text="Aktion")
        self.tree.heading("bildvergleich", text="Bildvergleich")
        
        # Spalten-Breite
        self.tree.column("quelle", width=180)
        self.tree.column("fundstellen", width=200)
        self.tree.column("status", width=120)
        self.tree.column("links", width=60)
        self.tree.column("aktion", width=100)
        self.tree.column("bildvergleich", width=120)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Event-Bindings - nur Single-Click
        self.tree.bind("<ButtonRelease-1>", self.on_case_single_click)
    
    def detect_click_column(self, event):
        """Ermittelt in welcher Spalte geklickt wurde"""
        region = self.tree.identify("region", event.x, event.y)
        print(f"   Region: {region}")
        print(f"   Event X/Y: {event.x}/{event.y}")
        
        if region == "cell":
            column = self.tree.identify("column", event.x, event.y)
            column_index = int(column[1:]) - 1  # #1 -> 0, #2 -> 1, etc.
            print(f"   Column String: {column}")
            print(f"   Column Index: {column_index}")
            return column_index
        else:
            print(f"   ❌ Nicht in Cell-Region")
            return None
    
    def get_link_indicators(self, case):
        """Ermittelt Link-Indikatoren für Quelle und Fundstelle"""
        quelle = case.get("quelle", "")
        fundstellen = case.get("fundstellen", "")
        
        # Prüfe ob Links (URLs) vorhanden sind
        quelle_is_url = quelle.startswith(('http://', 'https://'))
        fundstelle_is_url = fundstellen.startswith(('http://', 'https://'))
        
        # Generiere Ampel-Anzeige
        quelle_indicator = "🟢" if quelle_is_url else "🔴"
        fundstelle_indicator = "🟢" if fundstelle_is_url else "🔴"
        
        return f"{quelle_indicator}{fundstelle_indicator}"
    
    def on_case_single_click(self, event):
        """Einzelklick für spezifische Aktionsspalten"""     
        
        selection = self.tree.selection()
        if selection:
            column_index = self.detect_click_column(event)
            
            print(f"   Geklickte Spalte: {column_index}")
            print(f"   Event X/Y: {event.x}/{event.y}")
            
            # NUR reagieren bei Aktionsspalten 4 und 5
            if column_index not in [4, 5]:
                print(f"   ❌ Spalte {column_index} ignoriert")
                return
                
            item = self.tree.item(selection[0])
            case_index = int(item['tags'][0])
            
            print(f"   Case Index: {case_index}")
            
            # Spalte 4 = "aktion" (→ Bearbeiten)
            if column_index == 4:
                print(f"   ✅ BEARBEITEN-LINK - öffne Case Editor")
                self.parent.edit_case(case_index)
            # Spalte 5 = "bildvergleich" (🖼️ Bildvergleich)  
            elif column_index == 5:
                print(f"   ✅ BILDVERGLEICH-LINK - öffne Image Viewer")
                cases = self.data_service.get_cases()
                if case_index < len(cases):
                    case = cases[case_index]
                    self.parent.show_image_viewer_with_case(case)
        else:
            print(f"   ❌ Keine Selection")
    
    def edit_case(self, event=None):
        """Case bearbeiten (für Button-Klick)"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            case_index = int(item['tags'][0])
            self.parent.edit_case(case_index)
    
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
            links_display = self.get_link_indicators(case)
            
            self.tree.insert("", "end", values=(
                case.get("quelle", "")[:40] + "..." if len(case.get("quelle", "")) > 40 else case.get("quelle", ""),
                case.get("fundstellen", "")[:40] + "..." if len(case.get("fundstellen", "")) > 40 else case.get("fundstellen", ""),
                status_display,
                links_display,
                "→ Bearbeiten",
                "🖼️ Bildvergleich"
            ), tags=(str(i),))
    
    def edit_case(self, event=None):
        """Case bearbeiten (für Button-Klick)"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            case_index = int(item['tags'][0])
            self.parent.edit_case(case_index)
    
    def new_case(self):
        """Neuen Case erstellen - mit Validierung im Editor"""
        # Leeren Case erstellen und direkt zum Editor mit Validierung
        case_index = self.data_service.create_empty_case()
        if case_index is not None:
            from utils.logger import log_action
            log_action("GUI_ACTION", f"Neuer Case erstellt (Index: {case_index})")
            # Zum Case-Editor - dort ist bereits Validierung beim Speichern
            self.parent.edit_new_case(case_index)
    
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
