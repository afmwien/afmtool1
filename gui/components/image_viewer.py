"""
Image Viewer Komponente für AFMTool1
Side-by-side Bildvergleich mit automatischer Case-basierter Bildauswahl
"""
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import re
import requests
import hashlib
from pathlib import Path
from io import BytesIO

class ImageViewerComponent:
    """Image Viewer für Case-basierten Bildvergleich"""
    
    def __init__(self, parent):
        self.parent = parent
        self.data_service = parent.data_service
        
        # UI-Elemente
        self.image_viewer_frame = None
        self.quelle_display = None
        self.fundstelle_display = None
        self.left_label = None
        self.right_label = None
        self.left_canvas = None
        self.right_canvas = None
        
        # Image handling
        self.left_image = None
        self.right_image = None
        self.left_photo = None
        self.right_photo = None
        self.zoom_factor = 1.0
        
        # Case data
        self.current_case = None
        
    def create_view(self, container):
        """Image Viewer View erstellen"""
        self.image_viewer_frame = ttk.Frame(container)
        
        # Header
        header_frame = ttk.Frame(self.image_viewer_frame)
        header_frame.pack(fill="x", pady=(0, 20))
        
        title_label = ttk.Label(header_frame, text="🖼️ AFMTool1 - Bildvergleich", 
                               font=("Arial", 16, "bold"))
        title_label.pack()
        
        # Case Details Frame (wie im Case Editor)
        details_frame = ttk.LabelFrame(self.image_viewer_frame, text="📋 Case Details", padding=15)
        details_frame.pack(fill="x", pady=(0, 20))
        
        # Quelle
        ttk.Label(details_frame, text="Quelle:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w", pady=5)
        self.quelle_display = ttk.Label(details_frame, text="", foreground="blue")
        self.quelle_display.grid(row=0, column=1, sticky="w", padx=(10, 0), pady=5)
        
        # Fundstellen
        ttk.Label(details_frame, text="Fundstellen:", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky="w", pady=5)
        self.fundstelle_display = ttk.Label(details_frame, text="", foreground="blue")
        self.fundstelle_display.grid(row=1, column=1, sticky="w", padx=(10, 0), pady=5)
        
        # Control Panel
        control_frame = ttk.Frame(self.image_viewer_frame)
        control_frame.pack(fill="x", pady=(0, 10))
        
        # Buttons
        ttk.Button(control_frame, text="🔙 Zurück zum Case Editor", 
                  command=self.back_to_case_editor).pack(side="left", padx=(0, 20))
        
        ttk.Button(control_frame, text="🔄 Bilder neu laden", 
                  command=self.reload_case_images).pack(side="left", padx=(0, 10))
        
        ttk.Button(control_frame, text="📁 Quelle laden", 
                  command=self.load_left_image).pack(side="left", padx=(0, 10))
        ttk.Button(control_frame, text="📄 Fundstelle laden", 
                  command=self.load_right_image).pack(side="left", padx=(0, 10))
        ttk.Button(control_frame, text="🔄 Bilder tauschen", 
                  command=self.swap_images).pack(side="left", padx=(0, 20))
        
        # Zoom Controls
        ttk.Label(control_frame, text="Zoom:").pack(side="left", padx=(0, 5))
        ttk.Button(control_frame, text="➖", 
                  command=self.zoom_out).pack(side="left", padx=(0, 5))
        ttk.Button(control_frame, text="🔍", 
                  command=self.reset_zoom).pack(side="left", padx=(0, 5))
        ttk.Button(control_frame, text="➕", 
                  command=self.zoom_in).pack(side="left", padx=(0, 10))
        
        # Image Display Area
        display_frame = ttk.Frame(self.image_viewer_frame)
        display_frame.pack(fill="both", expand=True)
        
        # Left Panel
        left_panel = ttk.LabelFrame(display_frame, text="📁 Quelle", padding=10)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        self.left_label = ttk.Label(left_panel, text="Quelle noch nicht geladen", 
                                   foreground="gray")
        self.left_label.pack(pady=5)
        
        self.left_canvas = tk.Canvas(left_panel, bg="white", width=400, height=300)
        self.left_canvas.pack(fill="both", expand=True)
        
        # Right Panel
        right_panel = ttk.LabelFrame(display_frame, text="📄 Fundstelle", padding=10)
        right_panel.pack(side="right", fill="both", expand=True, padx=(5, 0))
        
        self.right_label = ttk.Label(right_panel, text="Fundstelle noch nicht geladen", 
                                    foreground="gray")
        self.right_label.pack(pady=5)
        
        self.right_canvas = tk.Canvas(right_panel, bg="white", width=400, height=300)
        self.right_canvas.pack(fill="both", expand=True)
        
        return self.image_viewer_frame
    
    def load_case_data(self, case):
        """Case-Daten laden und anzeigen"""
        self.current_case = case
        
        # Case Details anzeigen
        self.quelle_display.config(text=case.get("quelle", ""))
        self.fundstelle_display.config(text=case.get("fundstellen", ""))
        
        # Automatisch Bilder laden
        self.reload_case_images()
    
    def reload_case_images(self):
        """Beide Bilder basierend auf aktuellen Case-Daten neu laden"""
        if not self.current_case:
            return
        
        # Quelle laden - direkter Pfad oder Suche
        quelle_path = self.get_image_path_from_case_data(self.current_case.get("quelle", ""))
        if quelle_path:
            self.load_image_from_path(quelle_path, "left")
        
        # Fundstelle laden - direkter Pfad oder Suche  
        fundstelle_path = self.get_image_path_from_case_data(self.current_case.get("fundstellen", ""))
        if fundstelle_path:
            self.load_image_from_path(fundstelle_path, "right")
    
    def get_image_path_from_case_data(self, case_data):
        """Extrahiert Bildpfad direkt aus Case-Daten oder sucht nach Datei"""
        if not case_data:
            return None
        
        # Anführungszeichen entfernen falls vorhanden
        clean_data = case_data.strip('"\'')
        
        
        # 1. Prüfe ob URL (HTTP/HTTPS)
        if clean_data.startswith(('http://', 'https://')):
            return self.download_image_from_url(clean_data)
        
        # 2. Prüfe ob direkter Pfad zu Bilddatei
        if self.is_image_file(clean_data) and os.path.exists(clean_data):
            return clean_data
        
        # 3. Fallback: Text-basierte Suche in Standard-Verzeichnissen
        return self.search_image_in_directories(clean_data)
    
    def download_image_from_url(self, url):
        """Lädt Bild von URL herunter mit intelligentem Cache"""
        try:
            # Cache-Pfad generieren
            cache_path = self.get_cache_path(url)
            
            if cache_path.exists():
                return str(cache_path)
            
            # Headers für Browser-Simulation
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
                'Accept-Language': 'de-DE,de;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            # Download mit Browser-Headers
            response = requests.get(url, headers=headers, timeout=15, stream=True)
            response.raise_for_status()
            
            # Prüfe Content-Type
            content_type = response.headers.get('content-type', '')
            if not content_type.startswith('image/'):
                return None
            
            # Cache-Verzeichnis erstellen
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Bild herunterladen und speichern
            with open(cache_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            return str(cache_path)
            
        except requests.HTTPError as e:
            # Bei 403/510 alternative URL versuchen
            if e.response.status_code in [403, 510]:
                return self.try_alternative_download(url)
            return None
        except requests.RequestException as e:
            return None
        except Exception as e:
            return None
    
    def try_alternative_download(self, url):
        """Alternative Download-Methode bei Blockierung"""
        try:
            cache_path = self.get_cache_path(url)
            
            # Minimale Headers
            headers = {
                'User-Agent': 'AFMTool/1.0',
                'Accept': '*/*'
            }
            
            
            # Session für Cookies verwenden
            session = requests.Session()
            session.headers.update(headers)
            
            response = session.get(url, timeout=20, allow_redirects=True)
            response.raise_for_status()
            
            # Cache-Verzeichnis erstellen
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Bild speichern
            with open(cache_path, 'wb') as f:
                f.write(response.content)
            
            return str(cache_path)
            
        except Exception as e:
            return None
    
    def get_cache_path(self, url):
        """Generiert intelligenten Cache-Pfad für URL"""
        # Cache-Verzeichnis bestimmen
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        cache_dir = Path(base_dir) / "data" / "image_cache" / "downloads"
        
        # Domain extrahieren (ohne www.)
        try:
            domain = url.split('/')[2].replace('www.', '').replace(':', '_')
        except:
            domain = "unknown"
        
        # Dateinamen extrahieren
        try:
            filename = url.split('/')[-1]
            if '?' in filename:
                filename = filename.split('?')[0]
            if not filename or '.' not in filename:
                filename = "image.jpg"
        except:
            filename = "image.jpg"
        
        # Hash für Eindeutigkeit (erste 8 Zeichen)
        url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
        
        # Finaler Name: domain_filename_hash.ext
        name_parts = filename.split('.')
        if len(name_parts) > 1:
            name = f"{domain}_{name_parts[0]}_{url_hash}.{name_parts[-1]}"
        else:
            name = f"{domain}_{filename}_{url_hash}.jpg"
        
        # Lange Namen kürzen
        if len(name) > 100:
            name_base = name_parts[0][:30] if name_parts else "image"
            ext = name_parts[-1] if len(name_parts) > 1 else "jpg"
            name = f"{domain}_{name_base}_{url_hash}.{ext}"
        
        return cache_dir / name
    
    def is_image_file(self, filepath):
        """Prüft ob Dateiendung ein Bildformat ist"""
        if not filepath:
            return False
        return filepath.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.webp'))
    
    def search_image_in_directories(self, search_text):
        """Sucht Bild in Standard-Verzeichnissen basierend auf Text"""
        search_dirs = [
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "images", "quellen"),
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "images", "fundstellen")
        ]
        
        search_variants = self.get_search_variants(search_text)
        
        for search_dir in search_dirs:
            if not os.path.exists(search_dir):
                continue
            
            for filename in os.listdir(search_dir):
                if self.is_image_file(filename):
                    name_without_ext = os.path.splitext(filename)[0]
                    
                    for variant in search_variants:
                        if (variant.lower() in name_without_ext.lower() or 
                            name_without_ext.lower() in variant.lower() or
                            self.fuzzy_match(variant, name_without_ext)):
                            full_path = os.path.join(search_dir, filename)
                            return full_path
        
        return None
    
    def get_search_variants(self, text):
        """Erstelle verschiedene Suchvarianten basierend auf JSON Case-Daten"""
        if not text:
            return []
        
        variants = []
        
        # Prüfe ob es sich um einen Pfad handelt (wie in JSON: "C:\Users\...")
        if ('\\' in text and ':' in text) or ('/' in text and text.startswith('/')):
            # Extrahiere Dateinamen aus vollständigem Pfad
            if '\\' in text:
                filename = text.split('\\')[-1]
            else:
                filename = text.split('/')[-1]
            
            # Entferne Dateiendung
            if '.' in filename:
                filename = filename.rsplit('.', 1)[0]
                
            
            # Dateiname als Hauptvariante
            variants.append(filename)
            
            # Weitere Varianten aus Dateinamen
            if '-' in filename:
                # Teile bei Bindestrichen: "chatgpt-image-3-apr-2025" → ["chatgpt", "image"]
                parts = filename.split('-')[:3]  # Erste 3 Teile
                variants.extend(parts)
                variants.append('_'.join(parts))
            
            # Größe-Angaben entfernen: "1200x900" etc.
            clean_filename = re.sub(r'\d+x\d+', '', filename)
            clean_filename = re.sub(r'-\d+$', '', clean_filename)  # Zahlen am Ende
            if clean_filename != filename:
                variants.append(clean_filename)
                
        # Für normale Texte (Register-Namen etc.)
        else:
            
            # Variante 1: Erste wichtige Wörter
            words = [word for word in text.split() if len(word) > 2][:3]
            if words:
                variants.append('_'.join(words))
                variants.extend(words)  # Einzelne Wörter auch
            
            # Variante 2: Hauptwörter (länger als 3 Zeichen)
            main_words = [word for word in text.split() if len(word) > 3 and word.isalpha()][:2]
            if main_words:
                variants.append('_'.join(main_words))
                variants.extend(main_words)
            
            # Variante 3: Bereinigt ohne Sonderzeichen
            clean_text = re.sub(r'[^\w\s]', '', text)
            clean_text = re.sub(r'\s+', '_', clean_text.strip())
            if clean_text and len(clean_text) > 3:
                variants.append(clean_text[:20])
        
        # Bereinigung und Deduplizierung
        clean_variants = []
        for variant in variants:
            clean_variant = re.sub(r'[^\w_-]', '', str(variant))
            if clean_variant and len(clean_variant) > 2 and clean_variant not in clean_variants:
                clean_variants.append(clean_variant)
        
        return clean_variants[:8]  # Max 8 Varianten
    
    def fuzzy_match(self, search_term, filename):
        """Unscharfe Übereinstimmung"""
        search_lower = search_term.lower()
        file_lower = filename.lower()
        
        # Prüfe ob mindestens 70% der Zeichen übereinstimmen
        common_chars = sum(1 for c in search_lower if c in file_lower)
        return common_chars / len(search_lower) > 0.7
    
    def make_safe_filename(self, text):
        """Text in sicheren Dateinamen umwandeln"""
        if not text:
            return ""
        
        # Mehrere Varianten für bessere Erkennung
        safe_variants = []
        
        # Variante 1: Nur erste Wörter (erste 3-5 Wörter)
        words = text.split()[:5]
        if words:
            variant1 = "_".join(re.sub(r'[^\w]', '', word) for word in words if word)
            safe_variants.append(variant1[:30])
        
        # Variante 2: Komplett bereinigt, aber kürzer
        safe_text = re.sub(r'https?://[^\s]+', '', text)  # URLs entfernen
        safe_text = re.sub(r'[^\w\s-]', '', safe_text)  # Nur Buchstaben, Zahlen, Leerzeichen, Bindestriche
        safe_text = re.sub(r'\s+', '_', safe_text.strip())  # Leerzeichen durch Unterstriche
        safe_variants.append(safe_text[:30])
        
        # Variante 3: Nur Hauptwörter (länger als 3 Zeichen)
        main_words = [word for word in text.split() if len(word) > 3 and word.isalpha()][:3]
        if main_words:
            variant3 = "_".join(main_words)
            safe_variants.append(re.sub(r'[^\w_]', '', variant3)[:25])
        
        # Beste Variante zurückgeben (erste nicht-leere)
        for variant in safe_variants:
            if variant and len(variant) > 3:
                return variant
        
        # Fallback
        fallback = re.sub(r'[^\w]', '', text)[:20]
        return fallback
    
    def load_image_side(self, side):
        """Bild für bestimmte Seite laden (left/right)"""
        if side == "left":
            title = "Quelle-Bild auswählen"
            field_type = "quelle"
        else:
            title = "Fundstelle-Bild auswählen"
            field_type = "fundstelle"
        
        initial_dir = self.get_initial_directory_for_manual_load(field_type)
        
        filepath = filedialog.askopenfilename(
            title=title,
            initialdir=initial_dir,
            filetypes=[("Bilder", "*.png *.jpg *.jpeg *.bmp *.gif"), ("Alle Dateien", "*.*")]
        )
        if filepath:
            self.load_image_from_path(filepath, side)
    
    def load_left_image(self):
        """Linkes Bild (Quelle) manuell laden"""
        self.load_image_side("left")
    
    def load_right_image(self):
        """Rechtes Bild (Fundstelle) manuell laden"""
        self.load_image_side("right")
    
    def get_initial_directory_for_manual_load(self, field_type):
        """Bestimmt intelligentes Startverzeichnis für manuelles Laden"""
        # 1. Versuche Verzeichnis aus aktuellen Case-Daten zu extrahieren
        if self.current_case:
            field_key = "quelle" if field_type == "quelle" else "fundstellen"
            case_data = self.current_case.get(field_key, "")
            
            if case_data:
                clean_path = case_data.strip('"\'')
                if os.path.exists(clean_path) and os.path.isfile(clean_path):
                    return os.path.dirname(clean_path)
        
        # 2. Fallback zu Standard-Verzeichnissen
        base_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
        
        # Spezifische Verzeichnisse
        if field_type == "quelle":
            quelle_dir = os.path.join(base_dir, "images", "quellen")
            if os.path.exists(quelle_dir):
                return quelle_dir
        else:
            fundstelle_dir = os.path.join(base_dir, "images", "fundstellen")
            if os.path.exists(fundstelle_dir):
                return fundstelle_dir
        
        # Letzter Fallback
        return base_dir if os.path.exists(base_dir) else os.path.expanduser("~")
    
    def load_image_from_path(self, filepath, side):
        """Bild von Pfad laden"""
        try:
            image = Image.open(filepath)
            
            if side == "left":
                self.left_image = image
                self.left_label.config(text=f"📁 {os.path.basename(filepath)}")
                self.display_image(image, self.left_canvas)
            elif side == "right":
                self.right_image = image
                self.right_label.config(text=f"📄 {os.path.basename(filepath)}")
                self.display_image(image, self.right_canvas)
                
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Laden des Bildes: {str(e)}")
    
    def display_image(self, image, canvas):
        """Bild auf Canvas anzeigen"""
        if not image:
            return
            
        # Canvas-Größe holen
        canvas.update()
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            canvas_width, canvas_height = 400, 300
        
        # Bild skalieren
        img_width, img_height = image.size
        scale_x = (canvas_width - 20) / img_width
        scale_y = (canvas_height - 20) / img_height
        scale = min(scale_x, scale_y) * self.zoom_factor
        
        new_width = int(img_width * scale)
        new_height = int(img_height * scale)
        
        if new_width > 0 and new_height > 0:
            resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(resized_image)
            
            # Canvas leeren und Bild zentrieren
            canvas.delete("all")
            x = (canvas_width - new_width) // 2
            y = (canvas_height - new_height) // 2
            canvas.create_image(x, y, anchor="nw", image=photo)
            
            # Referenz behalten
            if canvas == self.left_canvas:
                self.left_photo = photo
            else:
                self.right_photo = photo
    
    def swap_images(self):
        """Bilder tauschen"""
        # Images tauschen
        self.left_image, self.right_image = self.right_image, self.left_image
        
        # Labels tauschen
        left_text = self.left_label.cget("text")
        right_text = self.right_label.cget("text")
        self.left_label.config(text=right_text)
        self.right_label.config(text=left_text)
        
        # Anzeige aktualisieren
        if self.left_image:
            self.display_image(self.left_image, self.left_canvas)
        else:
            self.left_canvas.delete("all")
            
        if self.right_image:
            self.display_image(self.right_image, self.right_canvas)
        else:
            self.right_canvas.delete("all")
    
    def adjust_zoom(self, direction):
        """Zoom anpassen (in oder out)"""
        if direction == "in":
            self.zoom_factor = min(self.zoom_factor * 1.2, 5.0)
        elif direction == "out":
            self.zoom_factor = max(self.zoom_factor / 1.2, 0.1)
        self.refresh_display()
    
    def zoom_in(self):
        """Hineinzoomen"""
        self.adjust_zoom("in")
    
    def zoom_out(self):
        """Herauszoomen"""
        self.adjust_zoom("out")
    
    def reset_zoom(self):
        """Zoom zurücksetzen"""
        self.zoom_factor = 1.0
        self.refresh_display()
    
    def refresh_display(self):
        """Anzeige aktualisieren"""
        if self.left_image:
            self.display_image(self.left_image, self.left_canvas)
        if self.right_image:
            self.display_image(self.right_image, self.right_canvas)
    
    def back_to_case_editor(self):
        """Zurück zum Case Editor"""
        self.parent.notebook.select(1)  # Tab 2 (Case Editor)
    
    def show(self):
        """Image Viewer anzeigen"""
        self.image_viewer_frame.pack(fill="both", expand=True)
    
    def hide(self):
        """Image Viewer ausblenden"""
        self.image_viewer_frame.pack_forget()
