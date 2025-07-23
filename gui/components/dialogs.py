"""
Dialog-Komponenten für AFMTool1
"""
import tkinter as tk
from tkinter import ttk, messagebox

class CaseInputDialog:
    """Dialog für neue Case-Eingabe"""
    
    def __init__(self, parent):
        self.result = None
        
        # Dialog-Fenster
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Neuer Case")
        self.dialog.geometry("500x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Zentrierung
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        # GUI-Elemente
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        ttk.Label(main_frame, text="📝 Neuen Case erstellen", font=("Arial", 14, "bold")).pack(pady=(0, 20))
        
        # Quelle
        ttk.Label(main_frame, text="Quelle:").pack(anchor="w", pady=(0, 5))
        self.quelle_entry = ttk.Entry(main_frame, width=60)
        self.quelle_entry.pack(fill="x", pady=(0, 15))
        self.quelle_entry.focus()
        
        # Fundstellen
        ttk.Label(main_frame, text="Fundstellen:").pack(anchor="w", pady=(0, 5))
        self.fundstellen_text = tk.Text(main_frame, height=5, width=60)
        self.fundstellen_text.pack(fill="both", expand=True, pady=(0, 20))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x")
        
        ttk.Button(button_frame, text="✅ Erstellen", command=self.ok_clicked).pack(side="right", padx=(10, 0))
        ttk.Button(button_frame, text="❌ Abbrechen", command=self.cancel_clicked).pack(side="right")
        
        # Enter-Binding
        self.dialog.bind('<Return>', lambda e: self.ok_clicked())
        self.dialog.bind('<Escape>', lambda e: self.cancel_clicked())
    
    def ok_clicked(self):
        quelle = self.quelle_entry.get().strip()
        fundstellen = self.fundstellen_text.get(1.0, tk.END).strip()
        
        if not quelle or not fundstellen:
            messagebox.showwarning("Eingabe", "Bitte füllen Sie alle Felder aus.")
            return
        
        self.result = (quelle, fundstellen)
        self.dialog.destroy()
    
    def cancel_clicked(self):
        self.dialog.destroy()
