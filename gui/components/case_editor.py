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
        self.edit_mode = False  # Toggle zwischen Anzeige- und Edit-Modus
        
        # Tracking für ungespeicherte Änderungen
        self.original_quelle = ""
        self.original_fundstellen = ""
        self.is_editing = False
        
        # UI-Elemente
        self.quelle_label = None
        self.quelle_entry = None
        self.fundstellen_label = None
        self.fundstellen_entry = None
        self.afm_text = None
        self.status_display_frame = None
        self.status_button_frame = None
        self.timestamps_text = None
        self.edit_button = None
        self.save_button = None
        self.cancel_button = None
        self.delete_button = None
        self.retreat_button = None
        self.advance_button = None
        
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
        
        # Quelle Entry (für Edit-Modus)
        self.quelle_entry = ttk.Entry(details_frame, width=50)
        
        # Fundstellen
        ttk.Label(details_frame, text="Fundstellen:", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky="w", pady=5)
        self.fundstellen_label = ttk.Label(details_frame, text="", foreground="blue")
        self.fundstellen_label.grid(row=1, column=1, sticky="w", padx=(10, 0), pady=5)
        
        # Fundstellen Entry (für Edit-Modus)
        self.fundstellen_entry = ttk.Entry(details_frame, width=50)
        
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
                  command=self.on_back_to_dashboard).pack(side="left")
        
        ttk.Button(action_frame, text="🖼️ Bildvergleich", 
                  command=self.open_image_comparison).pack(side="left", padx=(10, 0))
        
        # Edit-Modus Buttons
        self.edit_button = ttk.Button(action_frame, text="✏️ Bearbeiten", 
                                     command=self.toggle_edit_mode)
        self.edit_button.pack(side="left", padx=(10, 0))
        
        self.save_button = ttk.Button(action_frame, text="💾 Speichern", 
                                     command=self.save_changes)
        
        self.cancel_button = ttk.Button(action_frame, text="❌ Abbrechen", 
                                       command=self.cancel_edit)
        
        # Status-Workflow-Buttons - immer sichtbar, aber nur im Edit-Modus enabled
        self.retreat_button = ttk.Button(action_frame, text="⬅️ Zurück", 
                                        command=self.retreat_status,
                                        state="disabled")
        
        self.advance_button = ttk.Button(action_frame, text="➡️ Weiter", 
                                        command=self.advance_status,
                                        state="disabled")
        
        # Lösch-Button - immer sichtbar, aber nur im Edit-Modus enabled
        self.delete_button = ttk.Button(action_frame, text="🗑️ Löschen", 
                                       command=self.delete_case,
                                       state="disabled")  # Initial deaktiviert
        
        # Button-Layout: Links normal, rechts Workflow + Löschen
        # Bei side="right" werden die Buttons von rechts nach links eingefügt
        # Daher müssen wir in umgekehrter Reihenfolge packen
        self.delete_button.pack(side="right", padx=(0, 10))
        self.advance_button.pack(side="right", padx=(0, 5))
        self.retreat_button.pack(side="right", padx=(0, 5))
        
        # Tooltips für Buttons
        self.create_tooltip(self.retreat_button, 
                           "Status zurücksetzen (nur im Edit-Modus)")
        self.create_tooltip(self.advance_button, 
                           "Status weiterschalten (nur im Edit-Modus)")
        self.create_tooltip(self.delete_button, 
                           "Zum Löschen zuerst '✏️ Bearbeiten' anklicken")
        
        return self.case_edit_frame
    
    def create_tooltip(self, widget, text):
        """Einfacher Tooltip für Widgets"""
        def on_enter(event):
            if widget['state'] == 'disabled':
                # Tooltip nur bei deaktiviertem Button zeigen
                tooltip = tk.Toplevel()
                tooltip.wm_overrideredirect(True)
                tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
                
                label = tk.Label(tooltip, text=text, background="lightyellow", 
                               relief="solid", borderwidth=1, font=("Arial", 9))
                label.pack()
                
                widget.tooltip = tooltip
        
        def on_leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                del widget.tooltip
        
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
    
    def load_case(self, case_index):
        """Case laden und anzeigen"""
        self.selected_case_index = case_index
        self.edit_mode = False  # Immer im Anzeige-Modus starten
        
        # Edit-Status zurücksetzen beim Laden
        self.is_editing = False
        self.original_quelle = ""
        self.original_fundstellen = ""
        
        cases = self.data_service.get_cases()
        if case_index >= len(cases):
            return
            
        case = cases[case_index]
        
        # Details anzeigen
        self.quelle_label.config(text=case.get("quelle", ""))
        self.fundstellen_label.config(text=case.get("fundstellen", ""))
        
        # Entry-Felder mit Werten füllen (für Edit-Modus)
        self.quelle_entry.delete(0, tk.END)
        self.quelle_entry.insert(0, case.get("quelle", ""))
        self.fundstellen_entry.delete(0, tk.END)
        self.fundstellen_entry.insert(0, case.get("fundstellen", ""))
        
        # AFM-String anzeigen
        self.afm_text.config(state="normal")
        self.afm_text.delete(1.0, tk.END)
        self.afm_text.insert(1.0, case.get("afm_string", ""))
        self.afm_text.config(state="disabled")
        
        # Status-Workflow anzeigen
        self.update_status_workflow(case)
        
        # Zeitstempel anzeigen
        self.update_timestamps_display(case)
        
        # UI-Modus setzen
        self.update_ui_mode()
    
    def update_status_workflow(self, case):
        """Status-Workflow anzeigen (nur Anzeige, Buttons sind separat)"""
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
        
        # Button-Text und Status aktualisieren
        self.update_workflow_buttons(current_status)
    
    def update_workflow_buttons(self, current_status):
        """Workflow-Button-Text je nach aktuellem Status aktualisieren"""
        # Nur die ersten 3 Status sind manuell änderbar (NEU, Bearbeitung, Freigegeben)
        # "Abgeschlossen" kann nur durch automatische Archivierung erreicht werden
        statuses = ["erfassung", "verarbeitung", "validierung"]  # Ohne "archivierung"
        
        # Aktueller Index in der verkürzten Liste
        try:
            current_index = statuses.index(current_status)
        except ValueError:
            # Wenn Status "archivierung" ist, ist es nach der letzten verfügbaren Position
            current_index = len(statuses)
        
        # Zurück-Button Text (NEU ← Bearbeitung ← Freigegeben)
        if current_index > 0:
            previous_status = statuses[current_index - 1]
            previous_info = self.status_mapping[previous_status]
            self.retreat_button.config(text=f"⬅️ {previous_info['emoji']} {previous_info['name']}")
        else:
            self.retreat_button.config(text="⬅️ ---")
        
        # Weiter-Button Text (NEU → Bearbeitung → Freigegeben)
        if current_index < len(statuses) - 1:
            next_status = statuses[current_index + 1]
            next_info = self.status_mapping[next_status]
            self.advance_button.config(text=f"➡️ {next_info['emoji']} {next_info['name']}")
        else:
            self.advance_button.config(text="➡️ ---")
    
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
        """Status weiterschalten (vereinfacht, ohne Info-Dialog)"""
        if self.selected_case_index is not None:
            success = self.data_service.advance_case_status(self.selected_case_index)
            if success:
                self.refresh()
                from utils.logger import log_action
                log_action("GUI_ACTION", f"Status vorwärts gewechselt für Case {self.selected_case_index}")
    
    def retreat_status(self):
        """Status zurückschalten (vereinfacht, Felder bleiben bestehen)"""
        if self.selected_case_index is not None:
            success = self.data_service.retreat_case_status(self.selected_case_index)
            if success:
                self.refresh()
                from utils.logger import log_action
                log_action("GUI_ACTION", f"Status zurück gewechselt für Case {self.selected_case_index}")
    
    def delete_case(self):
        """Case löschen (nur im Edit-Modus verfügbar)"""
        if self.selected_case_index is None:
            return
            
        try:
            cases = self.data_service.get_cases()
            if self.selected_case_index >= len(cases):
                return
                
            case = cases[self.selected_case_index]
            
            # Bestätigung mit Case-Details
            result = messagebox.askyesno(
                "Case löschen",
                f"⚠️ ACHTUNG: Der Case wird permanent gelöscht!\n\n"
                f"Quelle: {case.get('quelle', '')}\n"
                f"Fundstellen: {case.get('fundstellen', '')}\n"
                f"Status: {self.data_service.get_case_status(case)}\n\n"
                f"Diese Aktion kann NICHT rückgängig gemacht werden!\n"
                f"Wirklich löschen?"
            )
            
            if result:
                success, deleted_case = self.data_service.delete_case(self.selected_case_index)
                if success:
                    from utils.logger import log_action
                    log_action("GUI_ACTION", f"Case {self.selected_case_index} gelöscht: {deleted_case.get('quelle', '')} (über Lösch-Button)")
                    
                    # Zurück zum Dashboard
                    self.parent.show_dashboard_view()
                else:
                    messagebox.showerror("Fehler", "Fehler beim Löschen des Cases!")
                    
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Löschen: {str(e)}")
    
    def clear_all_fields(self):
        """Alle Eingabefelder leeren"""
        # Quelle und Fundstellen Labels leeren
        if self.quelle_label:
            self.quelle_label.config(text="")
        if self.fundstellen_label:
            self.fundstellen_label.config(text="")
        
        # Entry-Felder leeren
        if self.quelle_entry:
            self.quelle_entry.delete(0, tk.END)
        if self.fundstellen_entry:
            self.fundstellen_entry.delete(0, tk.END)
        
        # AFM-String Text leeren
        if self.afm_text:
            self.afm_text.config(state="normal")
            self.afm_text.delete(1.0, tk.END)
            self.afm_text.config(state="disabled")
        
        # Zeitstempel Text leeren
        if self.timestamps_text:
            self.timestamps_text.config(state="normal")
            self.timestamps_text.delete(1.0, tk.END)
            self.timestamps_text.config(state="disabled")
        
        # Status-Workflow Frame leeren
        if self.status_display_frame:
            for widget in self.status_display_frame.winfo_children():
                widget.destroy()
        if self.status_button_frame:
            for widget in self.status_button_frame.winfo_children():
                widget.destroy()
    
    def refresh(self):
        """Case-Ansicht aktualisieren"""
        if self.selected_case_index is not None:
            self.load_case(self.selected_case_index)
    
    def toggle_edit_mode(self):
        """Zwischen Anzeige- und Edit-Modus wechseln"""
        self.edit_mode = not self.edit_mode
        
        # Tracking für Änderungen setzen
        if self.edit_mode:
            self.is_editing = True
            self.original_quelle = self.quelle_entry.get().strip() if self.quelle_entry else ""
            self.original_fundstellen = self.fundstellen_entry.get().strip() if self.fundstellen_entry else ""
        else:
            self.is_editing = False
            
        self.update_ui_mode()
    
    def update_ui_mode(self):
        """UI entsprechend dem aktuellen Modus aktualisieren"""
        if self.edit_mode:
            # Edit-Modus: Entry-Felder anzeigen
            self.quelle_label.grid_forget()
            self.fundstellen_label.grid_forget()
            
            self.quelle_entry.grid(row=0, column=1, sticky="w", padx=(10, 0), pady=5)
            self.fundstellen_entry.grid(row=1, column=1, sticky="w", padx=(10, 0), pady=5)
            
            # Buttons für Edit-Modus
            self.edit_button.pack_forget()
            self.save_button.pack(side="left", padx=(10, 0))
            self.cancel_button.pack(side="left", padx=(5, 0))
            
            # Workflow und Lösch-Buttons aktivieren
            self.retreat_button.config(state="normal")
            self.advance_button.config(state="normal")
            self.delete_button.config(state="normal")
            
            self.edit_button.config(text="👁️ Anzeigen")
        else:
            # Anzeige-Modus: Labels anzeigen
            self.quelle_entry.grid_forget()
            self.fundstellen_entry.grid_forget()
            
            self.quelle_label.grid(row=0, column=1, sticky="w", padx=(10, 0), pady=5)
            self.fundstellen_label.grid(row=1, column=1, sticky="w", padx=(10, 0), pady=5)
            
            # Buttons für Anzeige-Modus
            self.save_button.pack_forget()
            self.cancel_button.pack_forget()
            self.edit_button.pack(side="left", padx=(10, 0))
            
            # Workflow und Lösch-Buttons deaktivieren
            self.retreat_button.config(state="disabled")
            self.advance_button.config(state="disabled")
            self.delete_button.config(state="disabled")
            
            # Edit-Status zurücksetzen
            self.is_editing = False
            self.original_quelle = ""
            self.original_fundstellen = ""
            
            self.edit_button.config(text="✏️ Bearbeiten")
    
    def save_changes(self):
        """Änderungen speichern"""
        if self.selected_case_index is None:
            return
            
        try:
            # Aktuellen Case und Status holen
            cases = self.data_service.get_cases()
            if self.selected_case_index >= len(cases):
                return
                
            current_case = cases[self.selected_case_index]
            current_status = self.data_service.get_case_status(current_case)
            
            # Neue Werte aus Entry-Feldern holen
            new_quelle = self.quelle_entry.get().strip()
            new_fundstellen = self.fundstellen_entry.get().strip()
            
            if not new_quelle and not new_fundstellen:
                messagebox.showwarning("Eingabe", "Mindestens Quelle oder Fundstellen müssen eingegeben werden!")
                return
            
            # Prüfen ob sich die Werte geändert haben
            old_quelle = current_case.get("quelle", "")
            old_fundstellen = current_case.get("fundstellen", "")
            values_changed = (new_quelle != old_quelle) or (new_fundstellen != old_fundstellen)
            
            # Case aktualisieren
            success = self.data_service.update_case(self.selected_case_index, {
                "quelle": new_quelle,
                "fundstellen": new_fundstellen
            })
            
            if success:
                # Automatischer Status-Wechsel für neue Cases oder erste Bearbeitung
                is_first_edit = self.data_service.is_first_edit(self.selected_case_index)
                is_new_case = (old_quelle == "" and old_fundstellen == "")  # Neuer leerer Case
                
                if values_changed and (is_first_edit or is_new_case):
                    # Status automatisch auf "Bearbeitung" setzen
                    status_success = self.data_service.advance_case_status(self.selected_case_index)
                    if status_success:
                        from utils.logger import log_action
                        log_action("GUI_ACTION", f"Case {self.selected_case_index}: Automatischer Status-Wechsel NEU → Bearbeitung ({'neuer Case' if is_new_case else 'erste Bearbeitung'})")
                
                # AFM-String neu generieren
                self.data_service.regenerate_afm_string(self.selected_case_index)
                
                # Zurück zum Anzeige-Modus
                self.edit_mode = False
                self.is_editing = False
                self.original_quelle = ""
                self.original_fundstellen = ""
                self.refresh()
                
                # Logging
                from utils.logger import log_action
                log_action("GUI_ACTION", f"Case {self.selected_case_index} bearbeitet: Quelle='{new_quelle}', Fundstellen='{new_fundstellen}'")
                
                if values_changed and (is_first_edit or is_new_case):
                    if is_new_case:
                        messagebox.showinfo("Erfolg", 
                                          f"Neuer Case wurde erfolgreich erstellt!\n\n"
                                          f"Der Status wurde automatisch auf 'Bearbeitung' 🟡 gesetzt.\n"
                                          f"Ein Bearbeitungs-Zeitstempel wurde hinzugefügt.")
                    else:
                        messagebox.showinfo("Erfolg", 
                                          f"Änderungen wurden gespeichert!\n\n"
                                          f"Da dies die erste Bearbeitung war, wurde der Status\n"
                                          f"automatisch von 'NEU' 🔴 auf 'Bearbeitung' 🟡 gesetzt.\n\n"
                                          f"Ein Bearbeitungs-Zeitstempel wurde hinzugefügt.")
                else:
                    messagebox.showinfo("Erfolg", "Änderungen wurden gespeichert!")
            else:
                messagebox.showerror("Fehler", "Fehler beim Speichern der Änderungen!")
                
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Speichern: {str(e)}")
    
    def cancel_edit(self):
        """Bearbeitung abbrechen"""
        # Ursprüngliche Werte wiederherstellen
        if self.selected_case_index is not None:
            cases = self.data_service.get_cases()
            if self.selected_case_index < len(cases):
                case = cases[self.selected_case_index]
                self.quelle_entry.delete(0, tk.END)
                self.quelle_entry.insert(0, case.get("quelle", ""))
                self.fundstellen_entry.delete(0, tk.END)
                self.fundstellen_entry.insert(0, case.get("fundstellen", ""))
        
        # Zurück zum Anzeige-Modus
        self.edit_mode = False
        self.update_ui_mode()
    
    def open_image_comparison(self):
        """Bildvergleich für aktuellen Case öffnen"""
        if self.selected_case_index is not None:
            cases = self.data_service.get_cases()
            if self.selected_case_index < len(cases):
                case = cases[self.selected_case_index]
                self.parent.show_image_viewer_with_case(case)
    
    def has_unsaved_changes(self):
        """Prüft ob ungespeicherte Änderungen vorhanden sind"""
        # Sicherheits-Checks
        if (not self.is_editing or 
            self.selected_case_index is None or 
            not self.quelle_entry or 
            not self.fundstellen_entry):
            return False
            
        try:
            current_quelle = self.quelle_entry.get().strip()
            current_fundstellen = self.fundstellen_entry.get().strip()
            
            return (current_quelle != self.original_quelle or 
                    current_fundstellen != self.original_fundstellen)
        except:
            # Bei Fehlern sicherheitshalber False zurückgeben
            return False

    def on_back_to_dashboard(self):
        """Zurück zum Dashboard mit Unsaved Changes Check"""
        if self.has_unsaved_changes():
            from tkinter import messagebox
            result = messagebox.askyesnocancel(
                "Ungespeicherte Änderungen",
                "Sie haben ungespeicherte Änderungen.\n\n"
                "Speichern: Ja\n"
                "Verwerfen: Nein\n"
                "Abbrechen: Abbruch"
            )
            
            if result is True:  # Ja - Speichern
                self.save_changes()
            elif result is False:  # Nein - Verwerfen
                self.is_editing = False
                self.original_quelle = ""
                self.original_fundstellen = ""
            else:  # None - Abbrechen
                return
                
        self.parent.show_dashboard_view()
    
    def show(self, case_index):
        """Case-Editor anzeigen"""
        self.case_edit_frame.pack(fill="both", expand=True)
        self.load_case(case_index)
    
    def hide(self):
        """Case-Editor ausblenden"""
        self.case_edit_frame.pack_forget()
