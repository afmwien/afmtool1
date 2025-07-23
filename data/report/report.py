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
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

class AFMReporter:
    def __init__(self):
        self.data_dir = Path("data")
        self.report_dir = self.data_dir / "temp_reports"
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
            import os
            project_root = Path(".")
            for file in project_root.iterdir():
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
            utils_path = Path("utils")
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
            data_path = Path("data")
            if data_path.exists():
                for file in data_path.iterdir():
                    if file.is_file() and file.suffix in ['.json', '.log']:
                        data_files.append(file.name)
        except:
            data_files = ['cases.json', 'afmtool.log']
        
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
            test_path = Path("test")
            if test_path.exists():
                for file in test_path.iterdir():
                    if file.is_file() and file.suffix == '.py':
                        test_files.append(file.name)
        except:
            test_files = ['afm_string_handler.py', 'simple_afm.py']
        
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
        """PDF-Report generieren im Querformat - überschreibt alte Version"""
        # Fester Dateiname - wird überschrieben
        pdf_path = self.report_dir / "afmtool_report_latest.pdf"
        
        doc = SimpleDocTemplate(str(pdf_path), pagesize=landscape(A4))
        styles = getSampleStyleSheet()
        story = []
        
        # Titel mit Zeitstempel
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        title = Paragraph("AFMTool1 - System Report", styles['Title'])
        subtitle = Paragraph(f"Generiert am: {timestamp}", styles['Normal'])
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
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(overview_table)
        story.append(Spacer(1, 20))
        
        # 2. Detaildaten mit dynamischen Spalten + AFM String
        story.append(Paragraph("2. Cases-Datenbank Details", styles['Heading2']))
        cases_data, columns = self.get_database_data("cases.json")
        
        if cases_data and columns:
            # AFM String für letzte Zeile berechnen
            last_case = cases_data[-1]
            afm_string = json.dumps(last_case, ensure_ascii=False)
            
            # Dynamische Tabellen-Header + AFM String Spalte
            cases_table_data = [['Nr.'] + [col.title() for col in columns] + ['AFM String']]
            
            for i, case in enumerate(cases_data, 1):
                row = [str(i)]
                for col in columns:
                    value = case.get(col, '-')
                    # Lange Strings kürzen für bessere Darstellung
                    if isinstance(value, str) and len(value) > 50:
                        value = value[:47] + "..."
                    row.append(str(value))
                
                # AFM String nur für letzte Zeile
                if i == len(cases_data):
                    row.append(afm_string[:50] + "..." if len(afm_string) > 50 else afm_string)
                else:
                    row.append('-')
                    
                cases_table_data.append(row)
            
            cases_table = Table(cases_table_data)
            cases_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
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
                os.startfile(str(pdf_path))
            elif os.name == 'posix':  # macOS und Linux
                subprocess.run(['open', str(pdf_path)])
            print(f"PDF geöffnet: {pdf_path}")
        except Exception as e:
            print(f"PDF konnte nicht geöffnet werden: {e}")
            print(f"Manuell öffnen: {pdf_path}")

def main():
    """Report-Funktionen testen"""
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

if __name__ == "__main__":
    main()
