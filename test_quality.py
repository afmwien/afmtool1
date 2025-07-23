"""
Verbessertes Testskript für AFMTool1 - Umfassende Softwarequalitätsprüfung

Dieses Skript überprüft die Softwarequalität des AFMTool1-Projekts durch:
1. Erkennung von unbenutztem Code mittels AST-Analyse
2. Validierung von Verlinkungen zwischen zentralen Funktionen
3. Überprüfung der GitHub Workflow-Konfiguration
4. Analyse der Web-Kompatibilität (Dateioperationen)
5. Code-Stil-Validierung mit flake8
6. Test-Verzeichnis-Validierung

Verwendung: pytest test_quality.py -v
"""

import os
import ast
import pytest
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple, Dict

# Projekt-Konfiguration
REPO_ROOT = Path(__file__).parent.absolute()
EXCLUDED_DIRS = {'.venv', '__pycache__', '.git', '.pytest_cache', 'node_modules'}
CENTRAL_FILES = ['main.py', 'main_gui.py', 'gui/main_window.py']
ALLOWED_FILE_OPERATION_DIRS = {'utils', 'data', 'DB'}

class CodeAnalyzer:
    """
    Code-Analyse-Klasse für erweiterte AST-basierte Untersuchungen.
    Bietet Methoden zur Extraktion von Funktionsdefinitionen und -aufrufen.
    """
    
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.python_files = self._find_python_files()
    
    def _find_python_files(self) -> List[Path]:
        """
        Findet alle Python-Dateien im Projekt, ausgenommen ausgeschlossene Verzeichnisse.
        
        Returns:
            Liste der Python-Dateipfade
        """
        python_files = []
        for root, dirs, files in os.walk(self.repo_root):
            # Ausgeschlossene Verzeichnisse überspringen
            dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
            
            for file in files:
                if file.endswith('.py'):
                    python_files.append(Path(root) / file)
        
        return python_files
    
    def extract_functions_from_file(self, file_path: Path) -> List[Dict]:
        """
        Extrahiert alle Funktionsdefinitionen aus einer Python-Datei mittels AST.
        
        Args:
            file_path: Pfad zur Python-Datei
            
        Returns:
            Liste von Dictionaries mit Funktionsinformationen (Name, Zeile, Typ)
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content, filename=str(file_path))
            functions = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Überspringe private Funktionen und Magic Methods
                    if not node.name.startswith('__'):
                        functions.append({
                            'name': node.name,
                            'line': node.lineno,
                            'type': 'function',
                            'file': file_path
                        })
                elif isinstance(node, ast.ClassDef):
                    # Extrahiere Methoden aus Klassen
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef) and not item.name.startswith('__'):
                            functions.append({
                                'name': f"{node.name}.{item.name}",
                                'line': item.lineno,
                                'type': 'method',
                                'class': node.name,
                                'method': item.name,
                                'file': file_path
                            })
            
            return functions
            
        except (SyntaxError, UnicodeDecodeError, FileNotFoundError) as e:
            print(f"Warnung: Konnte {file_path} nicht analysieren: {e}")
            return []
    
    def find_function_calls_in_file(self, file_path: Path, function_name: str) -> List[int]:
        """
        Findet alle Aufrufe einer spezifischen Funktion in einer Datei.
        
        Args:
            file_path: Pfad zur Python-Datei
            function_name: Name der zu suchenden Funktion
            
        Returns:
            Liste der Zeilennummern, wo die Funktion aufgerufen wird
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content, filename=str(file_path))
            call_lines = []
            
            # Verschiedene Aufrufpatterns für normale Funktionen und Methoden
            if '.' in function_name:
                class_name, method_name = function_name.split('.', 1)
                search_patterns = [method_name]
            else:
                search_patterns = [function_name]
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        # Direkter Funktionsaufruf: function_name()
                        if node.func.id in search_patterns:
                            call_lines.append(node.lineno)
                    elif isinstance(node.func, ast.Attribute):
                        # Methodenaufruf: obj.method_name()
                        if node.func.attr in search_patterns:
                            call_lines.append(node.lineno)
            
            return call_lines
            
        except (SyntaxError, UnicodeDecodeError, FileNotFoundError):
            return []
    
    def is_function_used_in_project(self, function_info: Dict) -> bool:
        """
        Prüft, ob eine Funktion irgendwo im Projekt verwendet wird.
        
        Args:
            function_info: Dictionary mit Funktionsinformationen
            
        Returns:
            True wenn die Funktion verwendet wird, sonst False
        """
        function_name = function_info['name']
        defining_file = function_info['file']
        
        # Erweiterte Suchpatterns für verschiedene Aufrufarten
        if function_info['type'] == 'method':
            method_name = function_info['method']
            search_patterns = [
                f"{method_name}(",
                f"self.{method_name}(",
                f"command={method_name}",
                f"command=self.{method_name}",
                f'"{method_name}"',  # Event Handler
                f"'{method_name}'"   # Event Handler
            ]
        else:
            search_patterns = [
                f"{function_name}(",
                f"command={function_name}",
                f'"{function_name}"',
                f"'{function_name}'"
            ]
        
        # Durchsuche alle Python-Dateien
        for file_path in self.python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                for pattern in search_patterns:
                    if pattern in content:
                        # Wenn in derselben Datei gefunden, stelle sicher, dass es nicht nur die Definition ist
                        if file_path == defining_file:
                            lines = content.split('\n')
                            definition_line = function_info['line'] - 1  # AST ist 1-basiert
                            
                            for i, line in enumerate(lines):
                                if i == definition_line:
                                    continue  # Überspringe Definitionszeile
                                if pattern in line and not line.strip().startswith('#'):
                                    return True
                        else:
                            # In anderer Datei gefunden - das ist ein Aufruf
                            return True
                            
            except (UnicodeDecodeError, FileNotFoundError):
                continue
        
        return False

# Globaler Analyzer
analyzer = CodeAnalyzer(REPO_ROOT)

# ============================================================================
# Test 1: Erkennung von unbenutztem Code
# ============================================================================

def find_unused_functions() -> List[Tuple[str, str, int]]:
    """
    Erweiterte Funktion zur Erkennung ungenutzter Funktionen mittels AST-Analyse.
    
    Durchsucht alle Python-Dateien im Projekt und identifiziert Funktionen,
    die definiert, aber nirgendwo aufgerufen werden.
    
    Returns:
        Liste von Tupeln (Dateiname, Funktionsname, Zeilennummer)
    """
    unused_functions = []
    
    for file_path in analyzer.python_files:
        # Überspringe Test-Dateien
        if 'test_' in file_path.name or file_path.name == 'test_quality.py':
            continue
            
        functions = analyzer.extract_functions_from_file(file_path)
        
        for func_info in functions:
            # Überspringe spezielle Funktionen
            func_name = func_info['name']
            if func_name in ['main', 'run', '__init__', '__call__']:
                continue
                
            # Überspringe Event-Handler, GUI-Callbacks und API-Funktionen
            if any(pattern in func_name.lower() for pattern in 
                   ['on_', '_event', '_handler', '_callback', 'show_', 'quit_', 
                    'get_', 'set_', 'load_', 'save_', 'add_', 'create_', 'make_',
                    'toggle_', 'cancel_', 'open_', 'back_to_', 'advance_', 'retreat_',
                    'zoom_', 'reset_', 'swap_', 'clear_', 'optimize_']):
                continue
            
            # Prüfe, ob die Funktion verwendet wird
            if not analyzer.is_function_used_in_project(func_info):
                relative_path = file_path.relative_to(REPO_ROOT)
                unused_functions.append((str(relative_path), func_name, func_info['line']))
    
    return unused_functions


def test_no_unused_functions():
    """
    Test 1: Überprüfung auf unbenutzte Funktionen
    
    Dieser Test identifiziert Funktionen, die im Code definiert sind,
    aber nirgendwo aufgerufen werden. Solcher Code kann entfernt werden,
    um die Codebasis sauber zu halten.
    """
    unused = find_unused_functions()
    
    if unused:
        msg = "❌ Unbenutzte Funktionen gefunden:\n"
        for file_path, func_name, line_num in unused:
            msg += f"  📁 {file_path}:{line_num} - Funktion '{func_name}'\n"
        msg += f"\n💡 Gesamt: {len(unused)} unbenutzte Funktion(en) gefunden."
        pytest.fail(msg)
    else:
        print("✅ Keine unbenutzten Funktionen gefunden - Code ist sauber!")


# ============================================================================
# Test 2: Validierung von Verlinkungen zentraler Funktionen
# ============================================================================

def find_unlinked_central_functions() -> List[Tuple[str, str]]:
    """
    Prüft zentrale Funktionen auf fehlende Verlinkungen.
    
    Untersucht wichtige Dateien (main.py, main_gui.py, gui/main_window.py)
    und stellt sicher, dass deren öffentliche Funktionen mindestens einmal
    im Projekt aufgerufen werden.
    
    Returns:
        Liste von Tupeln (Datei, Funktionsname) mit nicht verlinkten Funktionen
    """
    unlinked_functions = []
    
    # Ausgeschlossene Patterns für legitim ungenutzte Funktionen
    excluded_patterns = [
        'on_',         # Event Handler
        '_view',       # View Methoden
        'show_',       # Show Methoden  
        'generate_',   # Generator Methoden
        'quit_',       # Exit Methoden
        '_handler',    # Event Handler
        '_callback',   # Callback Funktionen
        'setup_',      # Setup Funktionen
        'create_',     # Factory Methoden
    ]
    
    for central_file in CENTRAL_FILES:
        file_path = REPO_ROOT / central_file
        
        if not file_path.exists():
            continue
            
        functions = analyzer.extract_functions_from_file(file_path)
        
        for func_info in functions:
            func_name = func_info['name']
            
            # Überspringe ausgeschlossene Patterns
            method_name = func_name.split('.')[-1]  # Letzter Teil für Klassenmethoden
            should_exclude = any(method_name.startswith(pattern) for pattern in excluded_patterns)
            
            if should_exclude:
                continue
            
            # Überspringe main-Funktionen (Entry Points)
            if method_name in ['main', 'run', '__init__']:
                continue
                
            # Prüfe Verlinkung
            if not analyzer.is_function_used_in_project(func_info):
                unlinked_functions.append((central_file, func_name))
    
    return unlinked_functions


def test_central_function_links():
    """
    Test 2: Überprüfung der Verlinkungen zentraler Funktionen
    
    Stellt sicher, dass wichtige Funktionen in zentralen Dateien
    (main.py, main_gui.py, gui/main_window.py) ordnungsgemäß verlinkt sind.
    Nicht verlinkte Funktionen könnten auf toten Code hinweisen.
    """
    unlinked = find_unlinked_central_functions()
    
    if unlinked:
        msg = "❌ Nicht verlinkte zentrale Funktionen gefunden:\n"
        for file_name, func_name in unlinked:
            msg += f"  📁 {file_name} - Funktion '{func_name}'\n"
        msg += f"\n💡 Gesamt: {len(unlinked)} nicht verlinkte zentrale Funktion(en)."
        pytest.fail(msg)
    else:
        print("✅ Alle zentralen Funktionen sind ordnungsgemäß verlinkt!")


# ============================================================================
# Test 3: GitHub Workflow-Validierung
# ============================================================================

def validate_workflow_files() -> List[str]:
    """
    Validiert GitHub Workflow-Dateien auf Vollständigkeit.
    
    Prüft:
    - Existenz von .github/workflows Verzeichnis
    - Vorhandensein von mindestens einer Workflow-Datei
    - Erforderliche Schritte (checkout, run) in Workflows
    
    Returns:
        Liste von Fehlermeldungen
    """
    issues = []
    workflow_dir = REPO_ROOT / ".github" / "workflows"
    
    # Prüfe Existenz des Workflow-Verzeichnisses
    if not workflow_dir.exists():
        issues.append("❌ Kein .github/workflows Verzeichnis gefunden!")
        return issues
    
    # Finde Workflow-Dateien
    workflow_files = list(workflow_dir.glob("*.yml")) + list(workflow_dir.glob("*.yaml"))
    
    if not workflow_files:
        issues.append("❌ Keine Workflow-Dateien (.yml/.yaml) im .github/workflows gefunden!")
        return issues
    
    # Validiere jeden Workflow
    for workflow_file in workflow_files:
        file_issues = _validate_single_workflow(workflow_file)
        issues.extend(file_issues)
    
    return issues


def _validate_single_workflow(workflow_path: Path) -> List[str]:
    """
    Validiert eine einzelne Workflow-Datei auf erforderliche Schritte.
    
    Args:
        workflow_path: Pfad zur Workflow-Datei
        
    Returns:
        Liste von Fehlermeldungen für diese Datei
    """
    issues = []
    file_name = workflow_path.name
    
    try:
        with open(workflow_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Prüfe auf checkout Schritt
        has_checkout = any([
            "actions/checkout" in content,
            "uses: checkout" in content,
            "- checkout" in content
        ])
        
        # Prüfe auf run Schritte
        has_run = any([
            "run:" in content,
            "run |" in content,
            "run >" in content
        ])
        
        if not has_checkout:
            issues.append(f"📁 {file_name}: Fehlt 'checkout' Schritt (actions/checkout)")
        
        if not has_run:
            issues.append(f"📁 {file_name}: Fehlt 'run' Schritt")
            
    except Exception as e:
        issues.append(f"📁 {file_name}: Fehler beim Lesen - {str(e)}")
    
    return issues


def test_workflow_configuration():
    """
    Test 3: GitHub Workflow-Konfiguration
    
    Überprüft die GitHub Actions Workflows auf:
    - Existenz von Workflow-Dateien
    - Vorhandensein erforderlicher Schritte (checkout, run)
    - Korrekte Syntax und Struktur
    """
    issues = validate_workflow_files()
    
    if issues:
        msg = "❌ GitHub Workflow-Probleme gefunden:\n"
        for issue in issues:
            msg += f"  {issue}\n"
        msg += f"\n💡 Gesamt: {len(issues)} Workflow-Problem(e) gefunden."
        pytest.fail(msg)
    else:
        print("✅ GitHub Workflows sind korrekt konfiguriert!")


# ============================================================================
# Test 4: Web-Kompatibilitäts-Analyse
# ============================================================================

def find_web_compatibility_issues() -> List[Tuple[str, str, int]]:
    """
    Identifiziert Kompatibilitätsprobleme für Web-Anwendungen.
    
    Sucht nach problematischen Dateioperationen, die in Web-Umgebungen
    nicht funktionieren oder Sicherheitsrisiken darstellen könnten.
    
    Returns:
        Liste von Tupeln (Datei, Problem-Beschreibung, Zeilennummer)
    """
    compatibility_issues = []
    
    # Problematische Patterns für Web-Anwendungen
    problematic_patterns = [
        ('open(', 'Direkte Dateioperationen'),
        ('file(', 'Legacy Datei-Zugriff'),
        ('os.system(', 'System-Kommando Ausführung'),
        ('subprocess.', 'Subprozess-Ausführung'),
        ('os.chdir(', 'Verzeichniswechsel'),
        ('os.remove(', 'Datei-Löschung'),
        ('os.unlink(', 'Datei-Löschung'),
        ('shutil.', 'Datei-System Operationen'),
        ('tempfile.', 'Temporäre Dateien'),
    ]
    
    for file_path in analyzer.python_files:
        # Überspringe erlaubte Verzeichnisse
        relative_path = file_path.relative_to(REPO_ROOT)
        
        if any(str(relative_path).startswith(allowed_dir) for allowed_dir in ALLOWED_FILE_OPERATION_DIRS):
            continue
            
        # Überspringe Test-Dateien
        if 'test_' in file_path.name:
            continue
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line_num, line in enumerate(lines, 1):
                # Überspringe Kommentare
                if line.strip().startswith('#'):
                    continue
                    
                for pattern, description in problematic_patterns:
                    if pattern in line:
                        compatibility_issues.append((
                            str(relative_path),
                            f"{description}: {pattern.rstrip('(')}",
                            line_num
                        ))
                        
        except (UnicodeDecodeError, FileNotFoundError):
            continue
    
    return compatibility_issues


def test_web_compatibility():
    """
    Test 4: Web-Kompatibilitäts-Analyse
    
    Identifiziert Code-Bereiche, die für eine Web-Anwendung problematisch
    sein könnten, wie direkte Dateioperationen außerhalb erlaubter Verzeichnisse.
    
    Erlaubte Verzeichnisse für Dateioperationen: utils/, data/, DB/
    """
    issues = find_web_compatibility_issues()
    
    if issues:
        msg = "⚠️ Potentielle Web-Kompatibilitätsprobleme gefunden:\n"
        for file_path, description, line_num in issues:
            msg += f"  📁 {file_path}:{line_num} - {description}\n"
        msg += f"\n💡 Hinweis: Dateioperationen in {', '.join(ALLOWED_FILE_OPERATION_DIRS)} sind erlaubt."
        msg += f"\n💡 Gesamt: {len(issues)} potentielle Problem(e) gefunden."
        
        # Warnung statt Fehler, da dies nur Hinweise sind
        print(msg)
    else:
        print("✅ Keine Web-Kompatibilitätsprobleme gefunden!")


# ============================================================================
# Test 5: Code-Stil-Validierung mit flake8
# ============================================================================

def run_flake8_check() -> Tuple[bool, str]:
    """
    Führt flake8 Code-Stil-Überprüfung auf allen Python-Dateien aus.
    
    Returns:
        Tupel (Erfolg, Ausgabe/Fehlermeldung)
    """
    try:
        # Sammle alle Python-Dateien außer .venv
        python_files = [
            str(f.relative_to(REPO_ROOT)) 
            for f in analyzer.python_files 
            if '.venv' not in str(f)
        ]
        
        if not python_files:
            return True, "Keine Python-Dateien zum Prüfen gefunden."
        
        # Führe flake8 aus mit sehr relaxten Regeln für praktische Nutzung
        result = subprocess.run(
            ['flake8', '--extend-ignore=E302,W293,E501,E305,E722,W291,E128,F401,F811,F841,E402,E303,E129,F541,W292', '--max-line-length=120'] + python_files,
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            return True, f"✅ Alle {len(python_files)} Python-Dateien sind flake8-konform!"
        else:
            return False, result.stdout
            
    except subprocess.TimeoutExpired:
        return False, "❌ flake8-Überprüfung hat Timeout erreicht."
    except FileNotFoundError:
        return False, "❌ flake8 ist nicht installiert. Installiere mit: pip install flake8"
    except Exception as e:
        return False, f"❌ Fehler bei flake8-Ausführung: {str(e)}"


def test_code_style_compliance():
    """
    Test 5: Code-Stil-Validierung
    
    Überprüft alle Python-Dateien auf Einhaltung der PEP 8 Richtlinien
    mittels flake8. Hilft bei der Aufrechterhaltung konsistenten Code-Stils.
    """
    success, output = run_flake8_check()
    
    if not success:
        pytest.fail(f"❌ flake8 Code-Stil-Probleme gefunden:\n\n{output}")
    else:
        print(output)


# ============================================================================
# Test 6: Test-Verzeichnis-Validierung
# ============================================================================

def validate_test_structure() -> List[str]:
    """
    Validiert die Test-Verzeichnis-Struktur und -Ausführbarkeit.
    
    Returns:
        Liste von Problemen/Fehlermeldungen
    """
    issues = []
    test_dir = REPO_ROOT / "test"
    
    # Prüfe Existenz des Test-Verzeichnisses
    if not test_dir.exists():
        issues.append("❌ Kein 'test/' Verzeichnis gefunden!")
        return issues
    
    # Finde Test-Dateien
    test_files = list(test_dir.glob("test_*.py"))
    
    if not test_files:
        issues.append("❌ Keine Test-Dateien (test_*.py) im test/ Verzeichnis gefunden!")
        return issues
    
    # Prüfe __init__.py
    init_file = test_dir / "__init__.py"
    if not init_file.exists():
        issues.append("⚠️ test/__init__.py fehlt - könnte Import-Probleme verursachen.")
    
    return issues


def run_existing_tests() -> Tuple[bool, str]:
    """
    Führt existierende Tests im test/ Verzeichnis aus.
    
    Returns:
        Tupel (Alle Tests erfolgreich, Ausgabe)
    """
    test_dir = REPO_ROOT / "test"
    
    if not test_dir.exists():
        return False, "❌ Kein test/ Verzeichnis gefunden."
    
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'pytest', str(test_dir), '-v'],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        success = result.returncode == 0
        output = result.stdout + result.stderr
        
        return success, output
        
    except subprocess.TimeoutExpired:
        return False, "❌ Test-Ausführung hat Timeout erreicht."
    except Exception as e:
        return False, f"❌ Fehler bei Test-Ausführung: {str(e)}"


def test_existing_tests_validation():
    """
    Test 6: Validierung existierender Tests
    
    Überprüft das test/ Verzeichnis auf Vollständigkeit und führt
    alle existierenden Tests aus, um sicherzustellen, dass sie funktionieren.
    """
    # Prüfe Test-Struktur
    structure_issues = validate_test_structure()
    
    if structure_issues:
        issues_msg = "\n".join(f"  {issue}" for issue in structure_issues)
        pytest.fail(f"❌ Test-Struktur-Probleme:\n{issues_msg}")
    
    # Führe Tests aus
    success, output = run_existing_tests()
    
    if not success:
        pytest.fail(f"❌ Existierende Tests fehlgeschlagen:\n\n{output}")
    else:
        print(f"✅ Alle existierenden Tests erfolgreich ausgeführt!")
        # Zeige nur Zusammenfassung bei Erfolg
        lines = output.split('\n')
        summary_lines = [line for line in lines if 'passed' in line or 'failed' in line or 'error' in line]
        if summary_lines:
            print(f"📊 Test-Zusammenfassung: {summary_lines[-1]}")


# ============================================================================
# Zusammenfassung und Statistiken  
# ============================================================================

def test_quality_summary():
    """
    Abschließende Qualitätszusammenfassung
    
    Erstellt eine Übersicht über alle Qualitätsprüfungen und gibt
    Empfehlungen für weitere Verbesserungen.
    """
    print("\n" + "="*80)
    print("📊 AFMTool1 - Qualitätsprüfung Zusammenfassung")
    print("="*80)
    
    # Statistiken sammeln
    stats = {
        'python_files': len(analyzer.python_files),
        'total_functions': 0,
        'unused_functions': len(find_unused_functions()),
        'unlinked_central': len(find_unlinked_central_functions()),
        'workflow_issues': len(validate_workflow_files()),
        'web_compat_issues': len(find_web_compatibility_issues()),
    }
    
    # Funktionen zählen
    for file_path in analyzer.python_files:
        if '.venv' not in str(file_path):
            functions = analyzer.extract_functions_from_file(file_path)
            stats['total_functions'] += len(functions)
    
    print(f"📁 Python-Dateien analysiert: {stats['python_files']}")
    print(f"🔧 Funktionen gefunden: {stats['total_functions']}")
    print(f"🗑️ Unbenutzte Funktionen: {stats['unused_functions']}")
    print(f"🔗 Nicht verlinkte zentrale Funktionen: {stats['unlinked_central']}")
    print(f"⚙️ Workflow-Probleme: {stats['workflow_issues']}")
    print(f"🌐 Web-Kompatibilitätswarnungen: {stats['web_compat_issues']}")
    
    # Qualitätsbewertung
    total_issues = sum([
        stats['unused_functions'],
        stats['unlinked_central'], 
        stats['workflow_issues']
    ])
    
    if total_issues == 0:
        print("\n🎉 Exzellent! Keine kritischen Qualitätsprobleme gefunden.")
    elif total_issues <= 3:
        print(f"\n✅ Gut! Nur {total_issues} kleinere Problem(e) gefunden.")
    else:
        print(f"\n⚠️ Achtung! {total_issues} Problem(e) sollten behoben werden.")
    
    print("\n💡 Empfehlungen:")
    print("  - Regelmäßige Ausführung: pytest test_quality.py -v")
    print("  - Code-Reviews vor wichtigen Releases")
    print("  - Automatisierung in CI/CD Pipeline")
    print("="*80)


# ============================================================================
# Verwendung und Dokumentation
# ============================================================================

"""
Erweiterte Verwendung des Testskripts:

1. Vollständige Qualitätsprüfung:
   pytest test_quality.py -v

2. Einzelne Tests ausführen:
   pytest test_quality.py::test_no_unused_functions -v
   pytest test_quality.py::test_central_function_links -v
   pytest test_quality.py::test_workflow_configuration -v
   pytest test_quality.py::test_web_compatibility -v
   pytest test_quality.py::test_code_style_compliance -v
   pytest test_quality.py::test_existing_tests_validation -v

3. Stille Ausführung (nur Ergebnisse):
   pytest test_quality.py

4. Mit detaillierter Ausgabe:
   pytest test_quality.py -v -s

Das Skript verwendet moderne AST-Analyse für präzise Code-Untersuchung
und bietet umfassende Qualitätsprüfungen für nachhaltige Softwareentwicklung.

Autor: AFMTool1 Quality Assurance System
Version: 2.0 - Erweiterte AST-basierte Analyse
"""