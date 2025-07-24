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
        
        # Haupt-Container: Tabelle links, Konflikt-Panel rechts
        main_container = ttk.Frame(self.dashboard_frame)
        main_container.pack(fill="both", expand=True)
        
        # Case-Tabelle links
        self.table_frame = ttk.Frame(main_container)
        self.table_frame.pack(side="left", fill="both", expand=True)
        self.create_case_table()
        
        # Konflikt-Panel rechts (initial ausgeblendet)
        self.conflict_panel = ttk.Frame(main_container, width=300, relief="solid", borderwidth=1)
        self.create_conflict_panel()
        
        # Buttons
        button_frame = ttk.Frame(self.dashboard_frame)
        button_frame.pack(fill="x", pady=(20, 0))
        
        ttk.Button(button_frame, text="📝 Neuer Case", 
                  command=self.new_case).pack(side="left", padx=(0, 10))
        ttk.Button(button_frame, text="🔄 Aktualisieren", 
                  command=self.refresh_with_conflicts).pack(side="left", padx=(0, 10))
        ttk.Button(button_frame, text=" Report", 
                  command=self.parent.generate_report).pack(side="right", padx=(10, 0))
        ttk.Button(button_frame, text="❌ Beenden", 
                  command=self.parent.quit_app).pack(side="right")
        
        return self.dashboard_frame
    
    def create_case_table(self):
        """Case-Tabelle mit Treeview erstellen - erweitert um UUID und Fallnummer"""
        # Treeview - erweiterte Spalten mit Bildvergleich
        columns = ("uuid", "fallnummer", "quelle", "fundstellen", "status", "zeitstempel_count", "aktion", "bildvergleich", "konflikt")
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show="headings", height=15)
        
        # Spalten-Header
        self.tree.heading("uuid", text="UUID")
        self.tree.heading("fallnummer", text="Fallnummer")
        self.tree.heading("quelle", text="Quelle")
        self.tree.heading("fundstellen", text="Fundstellen")
        self.tree.heading("status", text="Status")
        self.tree.heading("zeitstempel_count", text="Zeitstempel")
        self.tree.heading("aktion", text="Aktion")
        self.tree.heading("bildvergleich", text="Bildvergleich")
        self.tree.heading("konflikt", text="Konflikt")
        
        # Spalten-Breite
        self.tree.column("uuid", width=70)
        self.tree.column("fallnummer", width=120)
        self.tree.column("quelle", width=160)
        self.tree.column("fundstellen", width=160)
        self.tree.column("status", width=100)
        self.tree.column("zeitstempel_count", width=80)
        self.tree.column("aktion", width=80)
        self.tree.column("bildvergleich", width=100)
        self.tree.column("konflikt", width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Event-Bindings
        self.tree.bind("<ButtonRelease-1>", self.on_case_single_click)
        self.tree.bind("<<TreeviewSelect>>", self.on_case_select)
    
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
        """Einzelklick für Aktionsspalten - Bearbeiten und Bildvergleich"""     
        
        selection = self.tree.selection()
        if selection:
            column_index = self.detect_click_column(event)
            
            print(f"   Geklickte Spalte: {column_index}")
            print(f"   Event X/Y: {event.x}/{event.y}")
            
            # Reaktion bei Aktionsspalten 6 (Bearbeiten) und 7 (Bildvergleich)
            if column_index not in [6, 7]:
                print(f"   ❌ Spalte {column_index} ignoriert - nur Aktion-Spalten (6,7) aktiv")
                return
                
            item = self.tree.item(selection[0])
            case_index = int(item['tags'][0])
            
            print(f"   Case Index: {case_index}")
            
            # Spalte 6 = "aktion" (→ Bearbeiten)
            if column_index == 6:
                print(f"   ✅ BEARBEITEN-LINK - öffne Case Editor")
                self.parent.edit_case(case_index)
            # Spalte 7 = "bildvergleich" (🖼️ Bildvergleich)  
            elif column_index == 7:
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
        """Tabelle mit Cases füllen - erweitert um UUID, Fallnummer und Status-Sortierung"""
        # Alte Einträge löschen
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Cases laden und mit fallnummer_verknuepfung.py verarbeiten
        cases = self.data_service.get_cases()
        
        # Status-Priorität für Sortierung
        status_priority = {
            "erfassung": 0,      # NEU - höchste Priorität
            "verarbeitung": 1,   # Bearbeitung
            "validierung": 2,    # Freigegeben
            "archivierung": 3    # Abgeschlossen - niedrigste Priorität
        }
        
        # Cases mit erweiterten Informationen erstellen
        enriched_cases = []
        for i, case in enumerate(cases):
            # UUID aus JSON oder generieren
            uuid = case.get("uuid", self.generate_uuid_fallback(case))
            
            # Fallnummer sicherstellen
            fallnummer = case.get("fallnummer", "LEER")
            if not fallnummer or fallnummer.strip() == "":
                fallnummer = f"AUTO-{uuid}"
            
            # Status ermitteln
            status = self.data_service.get_case_status(case)
            status_info = self.status_mapping[status]
            
            # Konflikt-Status prüfen
            konflikt_status = self._check_conflict_status(case)
            
            enriched_cases.append({
                "index": i,
                "case": case,
                "uuid": uuid,
                "fallnummer": fallnummer,
                "status": status,
                "status_priority": status_priority.get(status, 99),
                "status_display": f"{status_info['emoji']} {status_info['name']}",
                "zeitstempel_count": len(case.get("zeitstempel", [])),
                "conflict": konflikt_status
            })
        
        # Sortierung: 1. Status-Priorität, 2. Fallnummer
        enriched_cases.sort(key=lambda x: (x["status_priority"], x["fallnummer"]))
        
        # Tabelle füllen
        for case_data in enriched_cases:
            case = case_data["case"]
            
            self.tree.insert("", "end", values=(
                case_data["uuid"],
                case_data["fallnummer"],
                case.get("quelle", "")[:30] + "..." if len(case.get("quelle", "")) > 30 else case.get("quelle", ""),
                case.get("fundstellen", "")[:30] + "..." if len(case.get("fundstellen", "")) > 30 else case.get("fundstellen", ""),
                case_data["status_display"],
                case_data["zeitstempel_count"],
                "→ Bearbeiten",
                "🖼️ Bildvergleich",
                case_data["conflict"]
            ), tags=(str(case_data["index"]), case_data["conflict"]))
        
        # Tag-Konfiguration für Konflikte
        self.tree.tag_configure("conflict", background="#FFE6E6")  # Hellrot für Konflikte
        self.tree.tag_configure("no_conflict", background="white")
        
        print(f"✅ {len(enriched_cases)} Cases geladen und nach Status sortiert")
    
    def _check_conflict_status(self, case):
        """Prüft ob Case einen Konflikt hat"""
        if hasattr(self.data_service, 'conflict_data') and self.data_service.conflict_data:
            conflicts = self.data_service.conflict_data.get("conflicts", [])
            case_uuid = case.get("uuid")
            
            for conflict in conflicts:
                if conflict["uuid"] == case_uuid:
                    return "⚠️ KONFLIKT"
        
        return "✅ OK"
    
    def generate_uuid_fallback(self, case):
        """UUID-Fallback wenn nicht in JSON vorhanden"""
        import hashlib
        for ts in case.get("zeitstempel", []):
            if ts.startswith("erfassung:"):
                timestamp_part = ts.replace("erfassung:", "")
                hash_obj = hashlib.md5(timestamp_part.encode('utf-8'))
                return hash_obj.hexdigest()[:5].upper()
        return "ERROR"
    
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
    
    def refresh_with_conflicts(self):
        """Aktualisierung mit gleicher Logik wie GUI-Schließen (ohne Session-Beendigung)"""
        try:
            # Gleiche Merge-Logik wie sync_and_shutdown, aber ohne Session-Cleanup
            result = self.data_service.sync_session_data()
            
            if result[0] == "conflicts":
                # Konflikte gefunden - Tabelle neu laden mit Konflikt-Markierung
                self.populate_table()
                self.parent.show_message("⚠️ Konflikte", result[1])
            elif result[0]:
                # Erfolgreich ohne Konflikte
                self.populate_table()
                self.parent.show_message("✅ Aktualisiert", result[1])
            else:
                # Fehler
                self.parent.show_message("❌ Fehler", result[1])
                
        except Exception as e:
            self.parent.show_message("❌ Fehler", f"Aktualisierung fehlgeschlagen: {str(e)}")
    
    def resolve_conflict(self, event=None):
        """Löst Konflikt für ausgewählten Case"""
        selection = self.tree.selection()
        if not selection:
            return
            
        item = selection[0]
        values = self.tree.item(item, "values")
        
        if "KONFLIKT" in values[-1]:  # Konflikt-Spalte prüfen
            # Konflikt-Auflösung-Dialog anzeigen
            self._show_conflict_resolution_dialog(values[0])  # UUID übergeben

    def create_conflict_panel(self):
        """Erstellt das Side Panel für Konfliktauflösung"""
        # Panel-Header
        header = ttk.Label(self.conflict_panel, text="⚠️ Konfliktauflösung", 
                          font=("Arial", 12, "bold"))
        header.pack(pady=10)
        
        # Separator
        ttk.Separator(self.conflict_panel, orient="horizontal").pack(fill="x", pady=10)
        
        # Case-Info-Bereich
        self.case_info_frame = ttk.LabelFrame(self.conflict_panel, text="Case Details")
        self.case_info_frame.pack(fill="x", padx=10, pady=5)
        
        # Konflikt-Details-Bereich
        self.conflict_details_frame = ttk.LabelFrame(self.conflict_panel, text="Konflikt Details")
        self.conflict_details_frame.pack(fill="x", padx=10, pady=5)
        
        # Aktion-Buttons-Bereich
        self.action_frame = ttk.Frame(self.conflict_panel)
        self.action_frame.pack(fill="x", padx=10, pady=20)
        
        # Close-Button
        close_btn = ttk.Button(self.conflict_panel, text="❌ Schließen",
                              command=self.hide_conflict_panel)
        close_btn.pack(pady=10)
    
    def show_conflict_panel(self, case_uuid):
        """Zeigt das Konflikt-Panel für einen bestimmten Case"""
        # Panel einblenden
        self.conflict_panel.pack(side="right", fill="y", padx=(10, 0))
        
        # Case-Daten laden
        cases = self.data_service.get_cases()
        case = None
        for c in cases:
            if c.get("uuid") == case_uuid:
                case = c
                break
        
        if not case:
            return
        
        # Case-Info anzeigen
        self._populate_case_info(case)
        
        # Konflikt-Details anzeigen
        self._populate_conflict_details(case_uuid)
    
    def hide_conflict_panel(self):
        """Versteckt das Konflikt-Panel"""
        self.conflict_panel.pack_forget()
        # Case-Info und Konflikt-Details löschen
        for widget in self.case_info_frame.winfo_children():
            widget.destroy()
        for widget in self.conflict_details_frame.winfo_children():
            widget.destroy()
        for widget in self.action_frame.winfo_children():
            widget.destroy()
    
    def _populate_case_info(self, case):
        """Füllt das Case-Info-Panel"""
        ttk.Label(self.case_info_frame, text=f"UUID: {case.get('uuid', 'N/A')}", 
                 font=("Arial", 9, "bold")).pack(anchor="w", padx=5, pady=2)
        ttk.Label(self.case_info_frame, text=f"Fallnummer: {case.get('fallnummer', 'N/A')}").pack(anchor="w", padx=5, pady=1)
        
        quelle = case.get('quelle', 'N/A')
        if len(quelle) > 40:
            quelle = quelle[:40] + "..."
        ttk.Label(self.case_info_frame, text=f"Quelle: {quelle}").pack(anchor="w", padx=5, pady=1)
    
    def _populate_conflict_details(self, case_uuid):
        """Füllt das Konflikt-Details-Panel"""
        if not hasattr(self.data_service, 'conflict_data') or not self.data_service.conflict_data:
            ttk.Label(self.conflict_details_frame, text="Keine Konflikt-Daten verfügbar").pack(padx=5, pady=5)
            return
        
        conflicts = self.data_service.conflict_data.get("conflicts", [])
        conflict = None
        for c in conflicts:
            if c["uuid"] == case_uuid:
                conflict = c
                break
        
        if not conflict:
            ttk.Label(self.conflict_details_frame, text="Konflikt nicht gefunden").pack(padx=5, pady=5)
            return
        
        # Konflikt-Typ anzeigen
        ttk.Label(self.conflict_details_frame, text=f"Typ: {conflict.get('type', 'Unbekannt')}", 
                 font=("Arial", 9, "bold")).pack(anchor="w", padx=5, pady=2)
        
        # Zeitstempel-Vergleich
        local_time = conflict.get('local_timestamp', 'N/A')
        server_time = conflict.get('server_timestamp', 'N/A')
        
        ttk.Label(self.conflict_details_frame, text="Lokaler Zeitstempel:").pack(anchor="w", padx=5, pady=1)
        ttk.Label(self.conflict_details_frame, text=local_time, font=("Courier", 8)).pack(anchor="w", padx=10, pady=1)
        
        ttk.Label(self.conflict_details_frame, text="Server Zeitstempel:").pack(anchor="w", padx=5, pady=1)
        ttk.Label(self.conflict_details_frame, text=server_time, font=("Courier", 8)).pack(anchor="w", padx=10, pady=1)
        
        # Aktions-Buttons
        ttk.Button(self.action_frame, text="📥 Lokale Version behalten",
                  command=lambda: self._resolve_conflict(case_uuid, "keep_local")).pack(fill="x", pady=2)
        ttk.Button(self.action_frame, text="📤 Server Version übernehmen", 
                  command=lambda: self._resolve_conflict(case_uuid, "keep_server")).pack(fill="x", pady=2)
        ttk.Button(self.action_frame, text="🔄 Manuell zusammenführen",
                  command=lambda: self._resolve_conflict(case_uuid, "merge")).pack(fill="x", pady=2)
    
    def _resolve_conflict(self, case_uuid, action):
        """Löst den Konflikt mit der gewählten Aktion"""
        try:
            if hasattr(self.data_service, '_resolve_conflicts_visually'):
                result = self.data_service._resolve_conflicts_visually(case_uuid, action)
                if result:
                    self.parent.show_message("✅ Konflikt gelöst", f"Aktion '{action}' erfolgreich ausgeführt")
                    self.hide_conflict_panel()
                    self.refresh()
                else:
                    self.parent.show_message("❌ Fehler", "Konfliktauflösung fehlgeschlagen")
            else:
                self.parent.show_message("❌ Fehler", "Konfliktauflösung nicht verfügbar")
        except Exception as e:
            self.parent.show_message("❌ Fehler", f"Konfliktauflösung fehlgeschlagen: {str(e)}")
    
    def on_case_select(self, event):
        """Wird aufgerufen wenn ein Case ausgewählt wird"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            values = self.tree.item(item, "values")
            
            # Prüfen ob Case einen Konflikt hat
            if "KONFLIKT" in values[-1]:  # Konflikt-Spalte
                self.show_conflict_panel(values[0])  # UUID übergeben
            else:
                self.hide_conflict_panel()
    
    def show(self):
        """Dashboard anzeigen"""
        self.dashboard_frame.pack(fill="both", expand=True)
        self.refresh()
    
    def hide(self):
        """Dashboard ausblenden"""
        self.dashboard_frame.pack_forget()
