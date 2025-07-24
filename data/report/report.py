"""
AFMTool1 Report Generator
Erstellt Übersichten und PDF-Reports
"""

import json
import os
import datetime
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from reportlab.lib.pagesizes import A4, landscape, A3
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

# Try/Except Import mit Fallback für Fallnummer-Modul
try:
    import sys
    # Korrekter Pfad zu utils (3 Ebenen hoch vom report-Verzeichnis)
    utils_path = str(Path(__file__).parent.parent.parent / "utils")
    if utils_path not in sys.path:
        sys.path.insert(0, utils_path)
    from fallnummer_verknuepfung import find_fallnummer_groups
    USE_FALLNUMMER_MODULE = True
    print("✅ Fallnummer-Modul geladen")
except ImportError as e:
    print(f"⚠️ Fallback: Verwende eingebaute Gruppierung ({e})")
    USE_FALLNUMMER_MODULE = False

class AFMReporter:
    def __init__(self):
        # Pfad relativ zum Projekt-Root (zwei Ebenen hoch vom report-Verzeichnis)
        self.project_root = Path(__file__).parent.parent.parent
        self.data_dir = self.project_root / "data"
        self.report_dir = Path(__file__).parent / "temp_reports"
        self.databases = ["cases.json"]
        
    def get_database_overview(self):
        """1. Übersicht der bestehenden Datenbanken"""
        overview = {}
        # Nur die ursprüngliche Datenbank verarbeiten
        all_db_files = ["cases.json"]
        
        for db_file in all_db_files:
            db_path = self.data_dir / db_file
            if db_path.exists():
                with open(db_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Dynamische Erkennung der Struktur
                    if 'cases' in data:
                        records = len(data.get('cases', []))
                    else:
                        records = len(data) if isinstance(data, list) else 1
                    
                    overview[db_file] = {
                        "exists": True,
                        "size": db_path.stat().st_size,
                        "records": records,
                        "last_modified": datetime.datetime.fromtimestamp(
                            db_path.stat().st_mtime
                        ).strftime("%Y-%m-%d %H:%M:%S"),
                        "structure": self.analyze_structure(data)
                    }
            else:
                overview[db_file] = {"exists": False}
        return overview
    
    def analyze_structure(self, data):
        """Analysiert die Struktur der JSON-Daten"""
        if isinstance(data, dict):
            if 'cases' in data:
                structure = {"type": "cases_db", "fields": []}
                cases = data.get('cases', [])
                if cases and len(cases) > 0:
                    # Alle verfügbaren Spalten sammeln
                    all_fields = set()
                    for case in cases:
                        if isinstance(case, dict):
                            all_fields.update(case.keys())
                    structure["fields"] = sorted(list(all_fields))
                
                # Zusätzliche Felder auf Root-Level
                additional_fields = [k for k in data.keys() if k != 'cases']
                if additional_fields:
                    structure["additional"] = additional_fields
                return structure
            else:
                return {"type": "object", "keys": list(data.keys())}
        elif isinstance(data, list):
            return {"type": "array", "length": len(data)}
        else:
            return {"type": type(data).__name__}
    
    def calculate_optimal_pagesize_and_columns(self, headers):
        """
        Berechnet optimale Seitengröße und Spaltenbreiten basierend auf Überschriftenlänge
        
        Args:
            headers: Liste der Spaltenüberschriften
            
        Returns:
            tuple: (pagesize, spaltenbreiten)
        """
        # Minimale Breite pro Überschrift berechnen (ca. 8 Punkte pro Zeichen)
        min_widths = []
        for header in headers:
            # Mindestbreite: Überschriftenlänge * 8 + 20 Punkte Padding
            min_width = len(str(header)) * 8 + 20
            min_widths.append(max(min_width, 60))  # Mindestens 60 Punkte
        
        total_min_width = sum(min_widths) + 100  # +100 für Ränder
        
        # Papierformat wählen basierend auf benötigter Breite
        a4_landscape_width = landscape(A4)[0]  # ~842 Punkte
        a3_landscape_width = landscape(A3)[0]  # ~1191 Punkte
        
        if total_min_width <= a4_landscape_width:
            # A4 Querformat reicht aus
            pagesize = landscape(A4)
            available_width = a4_landscape_width - 100
        elif total_min_width <= a3_landscape_width:
            # A3 Querformat notwendig
            pagesize = landscape(A3)
            available_width = a3_landscape_width - 100
        else:
            # Noch größer: Custom Format
            custom_width = total_min_width + 100
            custom_height = landscape(A4)[1]  # Höhe von A4 beibehalten
            pagesize = (custom_width, custom_height)
            available_width = custom_width - 100
        
        # Spaltenbreiten proportional verteilen aber mindestens die berechnete Mindestbreite
        total_min = sum(min_widths)
        col_widths = []
        for min_width in min_widths:
            # Proportionale Verteilung der verfügbaren Breite
            width = (min_width / total_min) * available_width
            col_widths.append(max(width, min_width))
        
        return pagesize, col_widths

    def optimize_table_for_landscape(self, table_data, max_width):
        """
        Optimiert Tabellendaten für Querformat-Darstellung
        
        Args:
            table_data: Tabellendaten
            max_width: Maximale verfügbare Breite
            
        Returns:
            tuple: (optimierte_daten, spaltenbreiten)
        """
        if not table_data:
            return table_data, []
            
        # Anzahl der Spalten bestimmen
        num_cols = len(table_data[0]) if table_data else 0
        
        if num_cols <= 1:
            return table_data, [max_width]
        
        # Spaltenbreiten intelligent verteilen
        if num_cols <= 4:
            # Wenige Spalten: gleichmäßig verteilen
            col_width = max_width / num_cols
            return table_data, [col_width] * num_cols
        else:
            # Viele Spalten: erste Spalte (Nr.) schmal, Rest gleichmäßig
            nr_width = 50
            remaining_width = max_width - nr_width
            other_width = remaining_width / (num_cols - 1)
            return table_data, [nr_width] + [other_width] * (num_cols - 1)

    def truncate_text_to_column_width(self, text, max_chars):
        """
        Kürzt Text auf maximale Zeichenanzahl (abschneiden, nicht umbrechen)
        
        Args:
            text: Text zum Kürzen
            max_chars: Maximale Zeichenanzahl
            
        Returns:
            str: Gekürzter Text
        """
        if not isinstance(text, str):
            text = str(text)
        
        if len(text) <= max_chars:
            return text
        else:
            return text[:max_chars-3] + "..."

    def get_database_data(self, db_name):
        """2. Tabellarische Auflistung aller Daten je Datenbank mit dynamischen Spalten"""
        db_path = self.data_dir / db_name
        if not db_path.exists():
            return [], []
            
        with open(db_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        if 'cases' in data:
            cases = data.get('cases', [])
            if not cases:
                return [], []
            
            # Dynamische Spaltenerkennung
            all_columns = set()
            for case in cases:
                if isinstance(case, dict):
                    all_columns.update(case.keys())
            
            columns = sorted(list(all_columns))
            return cases, columns
        else:
            return [], []
    
    def generate_project_structure_chart(self):
        """3. Dynamische graphische Darstellung der Projektstruktur"""
        fig, ax = plt.subplots(1, 1, figsize=(14, 10))
        ax.set_xlim(0, 12)
        ax.set_ylim(0, 12)
        ax.axis('off')
        
        # Projekt-Root
        root_rect = mpatches.FancyBboxPatch((1, 10), 10, 1, boxstyle="round,pad=0.1", 
                                           facecolor='lightblue', edgecolor='black')
        ax.add_patch(root_rect)
        ax.text(6, 10.5, 'AFMTool1', ha='center', va='center', fontsize=14, weight='bold')
        
        # Automatische Datei-Erkennung im Hauptverzeichnis
        main_files = []
        try:
            # Relative zum Projekt-Root (nicht zum aktuellen Verzeichnis)
            for file in self.project_root.iterdir():
                if file.is_file() and file.suffix in ['.py', '.txt', '.md']:
                    main_files.append(file.name)
        except:
            main_files = ['main.py', 'requirements.txt', 'README.md']
        
        # Hauptdateien (dynamisch angeordnet)
        files_per_row = 4
        for i, file in enumerate(main_files[:8]):  # Max 8 Dateien anzeigen
            row = i // files_per_row
            col = i % files_per_row
            x = 0.5 + col * 2.8
            y = 8.5 - row * 0.9
            
            rect = mpatches.Rectangle((x, y), 2.5, 0.7, 
                                    facecolor='lightgreen', edgecolor='black')
            ax.add_patch(rect)
            ax.text(x + 1.25, y + 0.35, file, ha='center', va='center', fontsize=8)
        
        # Utils Package
        utils_rect = mpatches.FancyBboxPatch((0.5, 5.5), 3, 1.8, boxstyle="round,pad=0.1",
                                           facecolor='lightyellow', edgecolor='black')
        ax.add_patch(utils_rect)
        ax.text(2, 6.8, 'utils/', ha='center', va='center', fontsize=12, weight='bold')
        
        # Utils Dateien automatisch erkennen
        utils_files = []
        try:
            utils_path = self.project_root / "utils"
            if utils_path.exists():
                for file in utils_path.iterdir():
                    if file.is_file() and file.suffix == '.py':
                        utils_files.append(file.name)
        except:
            utils_files = ['database.py', 'logger.py']
        
        for i, file in enumerate(utils_files[:3]):
            ax.text(2, 6.4 - i*0.3, file, ha='center', va='center', fontsize=9)
        
        # Data Package mit automatischer Datenbank-Erkennung
        data_rect = mpatches.FancyBboxPatch((4.5, 5.5), 3.5, 1.8, boxstyle="round,pad=0.1",
                                          facecolor='lightcoral', edgecolor='black')
        ax.add_patch(data_rect)
        ax.text(6.25, 6.8, 'data/', ha='center', va='center', fontsize=12, weight='bold')
        
        # Automatische Erkennung aller JSON-Dateien und Log-Dateien
        data_files = []
        try:
            if self.data_dir.exists():
                for file in self.data_dir.iterdir():
                    if file.is_file() and file.suffix in ['.json', '.log']:
                        data_files.append(file.name)
            
            # Auch im logs-Verzeichnis nach Log-Dateien suchen
            logs_dir = self.project_root / "logs"
            if logs_dir.exists():
                for file in logs_dir.iterdir():
                    if file.is_file() and file.suffix == '.log':
                        data_files.append(f"logs/{file.name}")
                        
        except:
            data_files = ['cases.json', 'logs/afmtool.log']
        
        for i, file in enumerate(data_files[:4]):  # Max 4 Dateien
            color = 'red' if file.endswith('.json') else 'blue'
            ax.text(6.25, 6.4 - i*0.25, file, ha='center', va='center', fontsize=9, color=color, weight='bold')
        
        # Report System
        report_rect = mpatches.FancyBboxPatch((8.5, 5.5), 3, 1.8, boxstyle="round,pad=0.1",
                                            facecolor='lightsteelblue', edgecolor='black')
        ax.add_patch(report_rect)
        ax.text(10, 6.8, 'report/', ha='center', va='center', fontsize=12, weight='bold')
        ax.text(10, 6.4, 'report.py', ha='center', va='center', fontsize=9)
        ax.text(10, 6.1, 'temp_reports/', ha='center', va='center', fontsize=9)
        
        # Test System mit automatischer Datei-Erkennung
        test_rect = mpatches.FancyBboxPatch((2, 3), 4, 1.8, boxstyle="round,pad=0.1",
                                          facecolor='lightpink', edgecolor='black')
        ax.add_patch(test_rect)
        ax.text(4, 4.3, 'test/', ha='center', va='center', fontsize=12, weight='bold')
        
        # Test Dateien automatisch erkennen
        test_files = []
        try:
            test_path = self.project_root / "test"
            if test_path.exists():
                for file in test_path.iterdir():
                    if file.is_file() and file.suffix == '.py' and file.name != '__init__.py':
                        test_files.append(file.name)
        except:
            test_files = []
        
        # Falls keine Test-Dateien vorhanden, zeige Platzhalter
        if not test_files:
            test_files = ['[Keine Test-Dateien]']
        
        for i, file in enumerate(test_files[:3]):
            ax.text(4, 3.9 - i*0.25, file, ha='center', va='center', fontsize=8)
        
        # Legende für Datenbankdateien
        legend_rect = mpatches.Rectangle((6.5, 1.5), 4, 1, facecolor='white', edgecolor='black')
        ax.add_patch(legend_rect)
        ax.text(8.5, 2.2, 'Legende:', ha='center', va='center', fontsize=10, weight='bold')
        ax.text(7, 1.9, '● JSON Datenbanken', ha='left', va='center', fontsize=9, color='red')
        ax.text(7, 1.7, '● Log Dateien', ha='left', va='center', fontsize=9, color='blue')
        
        # Verbindungslinien
        ax.plot([6, 2], [10, 7.3], 'k-', alpha=0.5)
        ax.plot([6, 6.25], [10, 7.3], 'k-', alpha=0.5)
        ax.plot([6, 10], [10, 7.3], 'k-', alpha=0.5)
        ax.plot([6, 4], [10, 4.8], 'k-', alpha=0.5)
        
        # Titel mit Anzahl erkannter Datenbanken
        json_count = len([f for f in data_files if f.endswith('.json')])
        plt.title(f'AFMTool1 - Projektstruktur ({json_count} Datenbanken erkannt)', 
                 fontsize=16, weight='bold', pad=20)
        
        # Speichern - fester Dateiname (überschreibt alte Version)
        chart_path = self.report_dir / "project_structure_latest.png"
        plt.tight_layout()
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return chart_path
    
    def generate_pdf_report(self):
        """PDF-Report generieren mit festem A4 Querformat - überschreibt alte Version"""
        # Fester Dateiname - wird überschrieben
        pdf_path = self.report_dir / "afmtool_report_latest.pdf"
        
        # A4 Querformat verwenden
        doc = SimpleDocTemplate(str(pdf_path), pagesize=landscape(A4))
        styles = getSampleStyleSheet()
        story = []
        
        # Titel mit Zeitstempel - A3 Querformat
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        title = Paragraph("AFMTool1 - System Report", styles['Title'])
        subtitle = Paragraph(f"Generiert am: {timestamp} | Format: A4 Querformat", styles['Normal'])
        story.append(title)
        story.append(subtitle)
        story.append(Spacer(1, 20))
        
        # 1. Datenbank-Übersicht
        story.append(Paragraph("1. Datenbank-Übersicht", styles['Heading2']))
        overview = self.get_database_overview()
        
        overview_data = [['Datenbank', 'Status', 'Größe (Bytes)', 'Datensätze', 'Letzte Änderung']]
        for db_name, info in overview.items():
            if info['exists']:
                overview_data.append([
                    db_name, 
                    'Existiert', 
                    str(info['size']), 
                    str(info['records']),
                    info['last_modified']
                ])
            else:
                overview_data.append([db_name, 'Nicht gefunden', '-', '-', '-'])
        
        overview_table = Table(overview_data)
        overview_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),  # Linksbündig
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),  # Standard-Schriftgröße
            ('FONTSIZE', (0, 1), (-1, -1), 10),  # Standard-Schriftgröße für Datenzeilen
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # Vertikale Ausrichtung oben
        ]))
        # A4 Querformat: Angepasste Breite für Übersichtstabelle
        a4_landscape_width = landscape(A4)[0] - 100  # Abzüglich Ränder
        overview_table._argW = [a4_landscape_width * 0.25, a4_landscape_width * 0.15, 
                               a4_landscape_width * 0.15, a4_landscape_width * 0.15, 
                               a4_landscape_width * 0.3]  # Spaltenbreiten in Prozent
        
        story.append(overview_table)
        story.append(Spacer(1, 20))
        
        # 2. Detaildaten mit Matrix-View (Konzept 6: Doppel-Header mit Fallnummer-Gruppierung)
        story.append(Paragraph("2. Cases-Datenbank Matrix-View (gruppiert nach Fallnummer-Typen)", styles['Heading2']))
        cases_data, columns = self.get_database_data("cases.json")
        
        if cases_data and columns:
            # Gruppiere Cases mit Try/Except Fallback
            if USE_FALLNUMMER_MODULE:
                # Neue AFM-konforme Gruppierung
                fallnummer_data = find_fallnummer_groups(cases_data)
                groups = {}
                for fallnummer in fallnummer_data["exakte_gruppen"].keys():
                    groups[fallnummer] = [case for case in cases_data if case.get('fallnummer') == fallnummer]
            else:
                # Fallback: Alte eingebaute Logik
                groups = {}
                for case in cases_data:
                    fallnummer = case.get('fallnummer', '')
                    if fallnummer not in groups:
                        groups[fallnummer] = []
                    groups[fallnummer].append(case)
            
            # Erstelle doppelten Header: Gruppen-Header + Fallnummer-Header
            group_header = ['']  # Erste Spalte leer
            fallnummer_header = ['FallNr_client']
            
            sorted_cases = []
            for fallnummer in sorted(groups.keys()):
                group_cases = groups[fallnummer]
                sorted_cases.extend(group_cases)
                
                # Gruppenheader nur bei mehreren Cases mit gleicher Fallnummer
                if len(group_cases) > 1:
                    group_header.extend([fallnummer] + [''] * (len(group_cases) - 1))
                else:
                    group_header.extend([''])
                
                # Case-Header mit UUID (erfassung-Zeitstempel)
                for case in group_cases:
                    erfassung_uuid = ""
                    for ts in case['zeitstempel']:
                        if ts.startswith('erfassung:'):
                            erfassung_uuid = ts.split(':')[2]  # UUID-Teil
                            break
                    fallnummer_header.append(erfassung_uuid)
            
            # Beschränke auf 8 Fälle für A4-Querformat
            if len(sorted_cases) > 8:
                sorted_cases = sorted_cases[:8]
                group_header = group_header[:9]  # +1 für erste Spalte
                fallnummer_header = fallnummer_header[:9]
            
            table_data = [group_header, fallnummer_header]
            
            # A4 Querformat: Verfügbare Breite berechnen
            a4_landscape_width = landscape(A4)[0] - 100  # Verfügbare Breite
            
            # Info über verwendetes Format
            story.append(Paragraph(f"Matrix-View mit Doppel-Header: A4 Querformat für {len(sorted_cases)} Fälle", styles['Normal']))
            story.append(Spacer(1, 10))
            
            # Datenzeilen: Eigenschaften als Zeilen, Fälle als Spalten
            properties = ['UUID', 'Quelle', 'Fundstellen', 'Zeitschritte', 'AFM-Status']
            for prop in properties:
                row = [prop]
                for case in sorted_cases:
                    if prop == 'UUID':
                        row.append(case.get('fallnummer', '-'))
                    elif prop == 'Quelle':
                        value = case.get('quelle', '-')
                        row.append(value[:12] + '...' if len(value) > 12 else value)
                    elif prop == 'Fundstellen':
                        value = case.get('fundstellen', '-')
                        row.append(value[:12] + '...' if len(value) > 12 else value)
                    elif prop == 'Zeitschritte':
                        row.append(str(len(case.get('zeitstempel', []))))
                    elif prop == 'AFM-Status':
                        row.append('JSON-OK')
                table_data.append(row)
            
            # Tabelle erstellen
            cases_table = Table(table_data)
            
            # Spaltenbreiten für A4 berechnen
            num_cols = len(table_data[0]) if table_data else 1
            if num_cols > 1:
                first_col_width = a4_landscape_width * 0.15  # Eigenschafts-Spalte
                remaining_width = a4_landscape_width - first_col_width
                case_col_width = remaining_width / (num_cols - 1)
                col_widths = [first_col_width] + [case_col_width] * (num_cols - 1)
            else:
                col_widths = [a4_landscape_width]
            
            # Basis-Style für Matrix-View
            table_style = [
                ('BACKGROUND', (0, 0), (0, -1), colors.grey),  # Eigenschafts-Spalte
                ('BACKGROUND', (0, 0), (-1, 1), colors.lightgrey),  # Header-Zeilen
                ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 1), 'Helvetica-Bold'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]
            
            # Gruppenheader-Styling: Gruppierung durch Rahmen und Farben
            current_col = 1
            group_colors = [colors.lightblue, colors.lightgreen, colors.lightyellow, 
                           colors.lightcoral, colors.lightpink, colors.wheat, 
                           colors.lavender, colors.lightcyan]
            color_index = 0
            
            for prefix, group_cases in groups.items():
                if current_col < len(group_header):
                    group_size = min(len(group_cases), len(group_header) - current_col)
                    if group_size > 0:
                        # Gruppierung durch Farbe und Rahmen
                        group_color = group_colors[color_index % len(group_colors)]
                        table_style.append(('BACKGROUND', (current_col, 0), (current_col + group_size - 1, 0), group_color))
                        table_style.append(('BOX', (current_col, 0), (current_col + group_size - 1, -1), 2, colors.red))
                        color_index += 1
                    current_col += group_size
            
            cases_table.setStyle(TableStyle(table_style))
            cases_table._argW = col_widths
            
            story.append(cases_table)
                
        else:
            story.append(Paragraph("Keine Cases-Daten gefunden.", styles['Normal']))
        
        story.append(Spacer(1, 20))
        
        # 3. Projektstruktur
        story.append(Paragraph("3. Projektstruktur", styles['Heading2']))
        chart_path = self.generate_project_structure_chart()
        story.append(Paragraph(f"Projektstruktur-Diagramm gespeichert: {chart_path.name}", styles['Normal']))
        
        # Footer
        story.append(Spacer(1, 30))
        footer = Paragraph(f"Report generiert am: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
                          styles['Normal'])
        story.append(footer)
        
        # PDF erstellen
        doc.build(story)
        
        # PDF automatisch öffnen
        self.open_pdf(pdf_path)
        
        return pdf_path
    
    def open_pdf(self, pdf_path):
        """PDF automatisch öffnen"""
        import subprocess
        import os
        
        try:
            if os.name == 'nt':  # Windows
                # Verwende subprocess statt os.startfile für bessere Kontrolle
                subprocess.Popen(['start', '', str(pdf_path)], shell=True)
            elif os.name == 'posix':  # macOS und Linux
                subprocess.run(['open', str(pdf_path)])
            print(f"PDF geöffnet: {pdf_path}")
        except Exception as e:
            print(f"PDF konnte nicht automatisch geöffnet werden: {e}")
            print(f"Manuell öffnen: {pdf_path}")
            # Kein Fehler werfen, damit die Funktion normal beendet wird

def main():
    """Report-Funktionen testen"""
    try:
        reporter = AFMReporter()
        
        print("=== AFMTool1 Report Generator ===")
        print("\n1. Datenbank-Übersicht:")
        overview = reporter.get_database_overview()
        for db, info in overview.items():
            if info['exists']:
                print(f"  {db}: {info['records']} Datensätze, {info['size']} Bytes")
                if 'structure' in info:
                    struct = info['structure']
                    if struct.get('fields'):
                        print(f"    Spalten: {', '.join(struct['fields'])}")
                    if struct.get('additional'):
                        print(f"    Zusätzlich: {', '.join(struct['additional'])}")
            else:
                print(f"  {db}: Nicht gefunden")
        
        print("\n2. Generiere Projektstruktur-Diagramm...")
        chart_path = reporter.generate_project_structure_chart()
        print(f"  Gespeichert: {chart_path}")
        
        print("\n3. Generiere PDF-Report...")
        pdf_path = reporter.generate_pdf_report()
        print(f"  PDF-Report: {pdf_path}")
        
        print("\nReport-Generierung abgeschlossen!")
        
    except Exception as e:
        print(f"❌ Fehler bei der Report-Generierung: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    main()
