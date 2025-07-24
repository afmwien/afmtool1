"""
AFMTool1 - Erweiterte Code-Qualitätsprüfungen
Vollständig überarbeitetes Testskript mit zusätzlichen Prüfungen und optimierten bestehenden Tests.

⚡ Fortschrittsanzeige: Verbleibende Zeit ~2min

Qualitätsprüfungen:
1. ✅ Ungenutzte Funktionen mit verbesserter AST-Analyse
2. ✅ Fehlende Verlinkungen in zentralen Dateien  
3. ✅ Code-Duplikate Erkennung
4. ✅ Edge Cases Abdeckung
5. ✅ Dokumentationsqualität
6. ✅ Workflow-Validierung

Verwendung: pytest test_quality.py -v -s
"""

import os
import ast
import hashlib
import inspect
from typing import List, Dict, Tuple, Set, Any, Optional
from collections import defaultdict
from difflib import SequenceMatcher
import pytest

# Konfiguration
REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
CENTRAL_FILES = ["main.py", "main_gui.py", "gui/main_window.py"]
EXCLUDED_DIRS = {".venv", ".git", "__pycache__", ".pytest_cache", "logs", "data"}
MIN_DOCSTRING_LENGTH = 10
SIMILARITY_THRESHOLD = 0.8

# ============================================================================
# 1. UNGENUTZTE FUNKTIONEN - Verbesserte AST-Analyse
# ============================================================================

class FunctionAnalyzer:
    """Analysiert Funktionsdefinitionen und deren Verwendung mit AST."""
    
    def __init__(self, repo_root: str):
        self.repo_root = repo_root
        self.function_definitions = {}  # {file: [(func_name, lineno)]}
        self.function_calls = {}        # {file: [func_name]}
        self.imports = {}               # {file: [imported_names]}
        
    def analyze_project(self) -> List[Tuple[str, str]]:
        """Analysiert das gesamte Projekt und findet ungenutzte Funktionen."""
        # Sammle alle Funktionsdefinitionen und Aufrufe
        for python_file in self._get_python_files():
            self._analyze_file(python_file)
        
        # Finde ungenutzte Funktionen
        unused_functions = []
        excluded_patterns = {
            'on_', 'show_', 'hide_', 'get_', 'set_', 'create_', 'generate_',
            'quit_', 'exit_', '__init__', '__str__', '__repr__', 'main',
            'load_', 'save_', 'add_', 'new_', 'clear_', 'toggle_', 'cancel_',
            'open_', 'back_', 'advance_', 'retreat_', 'make_', 'swap_',
            'zoom_', 'reset_'
        }
        
        for file_path, functions in self.function_definitions.items():
            for func_name, lineno in functions:
                # Skip GUI/API functions that might be called via strings or events
                should_exclude = any(func_name.startswith(pattern) for pattern in excluded_patterns)
                if should_exclude:
                    continue
                    
                if not self._is_function_used(func_name, file_path):
                    rel_path = os.path.relpath(file_path, self.repo_root)
                    unused_functions.append((rel_path, func_name))
        
        return unused_functions
    
    def _get_python_files(self) -> List[str]:
        """Sammelt alle Python-Dateien im Projekt."""
        python_files = []
        for root, dirs, files in os.walk(self.repo_root):
            # Ausgeschlossene Verzeichnisse überspringen
            dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
            
            for file in files:
                if file.endswith(".py") and not file.startswith("test_"):
                    python_files.append(os.path.join(root, file))
        return python_files
    
    def _analyze_file(self, file_path: str):
        """Analysiert eine einzelne Python-Datei."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content, filename=file_path)
            
            # Sammle Funktionsdefinitionen
            functions = []
            calls = []
            imports = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if not node.name.startswith('_'):  # Ignoriere private Funktionen
                        functions.append((node.name, node.lineno))
                
                elif isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        calls.append(node.func.id)
                    elif isinstance(node.func, ast.Attribute):
                        calls.append(node.func.attr)
                
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    for alias in node.names:
                        imports.append(alias.name)
            
            self.function_definitions[file_path] = functions
            self.function_calls[file_path] = calls
            self.imports[file_path] = imports
            
        except Exception as e:
            print(f"Warnung: Fehler beim Analysieren von {file_path}: {e}")
    
    def _is_function_used(self, func_name: str, def_file: str) -> bool:
        """Prüft, ob eine Funktion irgendwo verwendet wird."""
        # Prüfe Aufrufe in allen Dateien
        for file_path, calls in self.function_calls.items():
            if func_name in calls:
                # Wenn in derselben Datei, prüfe ob es echte Aufrufe sind
                if file_path == def_file:
                    if self._has_real_calls_in_file(func_name, file_path):
                        return True
                else:
                    return True
        
        # Prüfe Importe (Funktion könnte importiert werden)
        for file_path, imports in self.imports.items():
            if func_name in imports:
                return True
        
        # Prüfe String-basierte Aufrufe (z.B. für GUI-Callbacks)
        return self._check_string_references(func_name)
    
    def _has_real_calls_in_file(self, func_name: str, file_path: str) -> bool:
        """Prüft, ob es echte Funktionsaufrufe in derselben Datei gibt."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            in_function_def = False
            for line in lines:
                stripped = line.strip()
                
                # Definition gefunden - überspringen
                if f"def {func_name}(" in stripped:
                    in_function_def = True
                    continue
                
                # Ende der Funktionsdefinition erkennen
                if in_function_def and stripped and not stripped.startswith(' ') and not stripped.startswith('\t'):
                    in_function_def = False
                
                # Aufruf außerhalb der Definition gefunden
                if not in_function_def and f"{func_name}(" in stripped and not stripped.startswith('#'):
                    return True
                    
        except Exception:
            pass
        
        return False
    
    def _check_string_references(self, func_name: str) -> bool:
        """Prüft String-basierte Referenzen (GUI-Callbacks, etc.)."""
        for file_path in self.function_calls.keys():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Suche nach String-Referenzen
                patterns = [f'"{func_name}"', f"'{func_name}'", f"command={func_name}"]
                for pattern in patterns:
                    if pattern in content:
                        return True
                        
            except Exception:
                continue
        
        return False

def test_no_unused_functions():
    """Test für ungenutzte Funktionen mit verbesserter AST-Analyse."""
    analyzer = FunctionAnalyzer(REPO_ROOT)
    unused_functions = analyzer.analyze_project()
    
    if unused_functions:
        print(f"\n⚠️  Potenziell ungenutzte Funktionen gefunden ({len(unused_functions)}):")
        for file_path, func_name in unused_functions:
            print(f"  - {file_path}: {func_name}")
        print("\n💡 Hinweis: Diese Funktionen könnten über String-Referenzen oder Events verwendet werden.")
    else:
        print("✅ Keine ungenutzten Funktionen gefunden.")

# ============================================================================
# 2. FEHLENDE VERLINKUNGEN - Erweiterte zentrale Dateien Analyse
# ============================================================================

class LinkageAnalyzer:
    """Analysiert Verlinkungen zwischen definierten Funktionen und deren Verwendung."""
    
    def __init__(self, repo_root: str, central_files: List[str]):
        self.repo_root = repo_root
        self.central_files = central_files
        self.excluded_patterns = {
            'on_', 'show_', 'hide_', 'get_', 'set_', 'create_', 'generate_',
            'quit_', 'exit_', '__init__', '__str__', '__repr__', 'main',
            'load_', 'save_', 'add_', 'new_', 'clear_', 'toggle_', 'cancel_',
            'open_', 'back_', 'advance_', 'retreat_', 'make_', 'swap_',
            'zoom_', 'reset_'
        }
    
    def analyze_missing_links(self) -> List[str]:
        """Analysiert fehlende Verlinkungen in zentralen Dateien."""
        missing_links = []
        
        for central_file in self.central_files:
            file_path = os.path.join(self.repo_root, central_file)
            if not os.path.exists(file_path):
                continue
            
            functions = self._extract_functions_from_file(file_path)
            for func_info in functions:
                if not self._should_exclude_function(func_info['name']):
                    if not self._is_function_linked(func_info, central_file):
                        missing_links.append(f"{central_file}: {func_info['name']}")
        
        return missing_links
    
    def _extract_functions_from_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Extrahiert Funktionsinformationen aus einer Datei."""
        functions = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content, filename=file_path)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append({
                        'name': node.name,
                        'lineno': node.lineno,
                        'args': [arg.arg for arg in node.args.args],
                        'returns': node.returns is not None
                    })
                elif isinstance(node, ast.ClassDef):
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            functions.append({
                                'name': f"{node.name}.{item.name}",
                                'lineno': item.lineno,
                                'args': [arg.arg for arg in item.args.args],
                                'returns': item.returns is not None,
                                'class': node.name
                            })
        
        except Exception as e:
            print(f"Warnung: Fehler beim Analysieren von {file_path}: {e}")
        
        return functions
    
    def _should_exclude_function(self, func_name: str) -> bool:
        """Prüft, ob eine Funktion von der Analyse ausgeschlossen werden soll."""
        method_name = func_name.split('.')[-1]
        return any(method_name.startswith(pattern) for pattern in self.excluded_patterns)
    
    def _is_function_linked(self, func_info: Dict[str, Any], source_file: str) -> bool:
        """Prüft, ob eine Funktion ordnungsgemäß verlinkt ist."""
        func_name = func_info['name']
        
        # Verschiedene Aufrufsmuster definieren
        if '.' in func_name:
            class_name, method_name = func_name.split('.', 1)
            search_patterns = [
                f"{method_name}(",
                f".{method_name}(",
                f"self.{method_name}(",
                f"command={method_name}",
                f'"{method_name}"',
                f"'{method_name}'"
            ]
        else:
            search_patterns = [
                f"{func_name}(",
                f"command={func_name}",
                f'"{func_name}"',
                f"'{func_name}'"
            ]
        
        # Durchsuche alle Python-Dateien
        for root, dirs, files in os.walk(self.repo_root):
            dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    if self._check_file_for_patterns(file_path, search_patterns, source_file):
                        return True
        
        return False
    
    def _check_file_for_patterns(self, file_path: str, patterns: List[str], source_file: str) -> bool:
        """Prüft eine Datei auf bestimmte Muster."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            for pattern in patterns:
                if pattern in content:
                    # Wenn es die gleiche Datei ist, prüfe auf echte Aufrufe
                    if os.path.basename(file_path) == os.path.basename(source_file):
                        return self._has_real_usage(content, pattern)
                    else:
                        return True
        except Exception:
            pass
        
        return False
    
    def _has_real_usage(self, content: str, pattern: str) -> bool:
        """Prüft, ob es echte Verwendung gibt (nicht nur Definition)."""
        lines = content.split('\n')
        pattern_base = pattern.split('(')[0].replace('"', '').replace("'", '')
        
        for line in lines:
            if pattern in line and not line.strip().startswith('#'):
                # Stelle sicher, dass es keine Funktionsdefinition ist
                if not f"def {pattern_base}" in line:
                    return True
        
        return False

def test_missing_links():
    """Test für fehlende Verlinkungen in zentralen Dateien."""
    analyzer = LinkageAnalyzer(REPO_ROOT, CENTRAL_FILES)
    missing_links = analyzer.analyze_missing_links()
    
    if missing_links:
        msg = "Fehlende Verlinkungen in zentralen Dateien gefunden:\n"
        for link in missing_links:
            msg += f"  - {link}\n"
        pytest.fail(msg)
    else:
        print("✅ Alle wichtigen Funktionen in zentralen Dateien sind ordnungsgemäß verlinkt.")

# ============================================================================
# 3. CODE-DUPLIKATE ERKENNUNG - AST-basierte Analyse
# ============================================================================

class DuplicateDetector:
    """Erkennt Code-Duplikate und ähnliche Funktionsimplementierungen."""
    
    def __init__(self, repo_root: str, similarity_threshold: float = SIMILARITY_THRESHOLD):
        self.repo_root = repo_root
        self.similarity_threshold = similarity_threshold
        self.functions = []  # [(file, func_name, ast_dump, code)]
    
    def find_duplicates(self) -> List[Tuple[str, str, str, str, float]]:
        """Findet Code-Duplikate im Projekt."""
        self._collect_functions()
        duplicates = []
        
        for i, (file1, func1, ast1, code1) in enumerate(self.functions):
            for j, (file2, func2, ast2, code2) in enumerate(self.functions[i+1:], i+1):
                similarity = self._calculate_similarity(ast1, ast2, code1, code2)
                
                if similarity >= self.similarity_threshold:
                    duplicates.append((file1, func1, file2, func2, similarity))
        
        return duplicates
    
    def _collect_functions(self):
        """Sammelt alle Funktionen im Projekt für Duplikatsprüfung."""
        for root, dirs, files in os.walk(self.repo_root):
            dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
            
            for file in files:
                if file.endswith('.py') and not file.startswith('test_'):
                    file_path = os.path.join(root, file)
                    self._extract_functions_from_file(file_path)
    
    def _extract_functions_from_file(self, file_path: str):
        """Extrahiert Funktionen aus einer Datei für Duplikatsprüfung."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content, filename=file_path)
            lines = content.split('\n')
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and not node.name.startswith('_'):
                    # Extrahiere Funktionscode
                    start_line = node.lineno - 1
                    end_line = node.end_lineno if hasattr(node, 'end_lineno') else start_line + 10
                    func_code = '\n'.join(lines[start_line:end_line])
                    
                    # AST-Dump für strukturellen Vergleich
                    ast_dump = ast.dump(node, annotate_fields=False)
                    
                    rel_path = os.path.relpath(file_path, self.repo_root)
                    self.functions.append((rel_path, node.name, ast_dump, func_code))
        
        except Exception as e:
            print(f"Warnung: Fehler beim Analysieren von {file_path}: {e}")
    
    def _calculate_similarity(self, ast1: str, ast2: str, code1: str, code2: str) -> float:
        """Berechnet Ähnlichkeit zwischen zwei Funktionen."""
        # AST-strukturelle Ähnlichkeit (70% Gewichtung)
        ast_similarity = SequenceMatcher(None, ast1, ast2).ratio()
        
        # Code-Ähnlichkeit (30% Gewichtung)
        code_similarity = SequenceMatcher(None, code1, code2).ratio()
        
        return ast_similarity * 0.7 + code_similarity * 0.3

def test_no_code_duplicates():
    """Test für Code-Duplikate - informativ."""
    detector = DuplicateDetector(REPO_ROOT)
    duplicates = detector.find_duplicates()
    
    if duplicates:
        print(f"\n🔍 Code-Duplikate gefunden ({len(duplicates)}):")
        for file1, func1, file2, func2, similarity in duplicates:
            if similarity >= 0.95:  # Sehr hohe Ähnlichkeit
                emoji = "🔴"
            elif similarity >= 0.85:  # Hohe Ähnlichkeit
                emoji = "🟡"
            else:  # Moderate Ähnlichkeit
                emoji = "🟢"
            print(f"  {emoji} {file1}:{func1} ↔ {file2}:{func2} (Ähnlichkeit: {similarity:.2%})")
        print("\n💡 Überprüfen Sie, ob diese Funktionen refaktoriert werden können.")
    else:
        print("✅ Keine Code-Duplikate gefunden.")

# ============================================================================
# 4. EDGE CASES ABDECKUNG - Funktionsanalyse
# ============================================================================

class EdgeCaseAnalyzer:
    """Analysiert Funktionen auf unzureichende Edge Case Abdeckung."""
    
    def __init__(self, repo_root: str):
        self.repo_root = repo_root
        self.edge_case_suggestions = {}
    
    def analyze_edge_cases(self) -> Dict[str, List[str]]:
        """Analysiert Funktionen und erstellt Edge Case Vorschläge."""
        functions_with_suggestions = {}
        
        for root, dirs, files in os.walk(self.repo_root):
            dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
            
            for file in files:
                if file.endswith('.py') and not file.startswith('test_'):
                    file_path = os.path.join(root, file)
                    file_suggestions = self._analyze_file_for_edge_cases(file_path)
                    if file_suggestions:
                        rel_path = os.path.relpath(file_path, self.repo_root)
                        functions_with_suggestions[rel_path] = file_suggestions
        
        return functions_with_suggestions
    
    def _analyze_file_for_edge_cases(self, file_path: str) -> List[str]:
        """Analysiert eine Datei für Edge Case Möglichkeiten."""
        suggestions = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content, filename=file_path)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and not node.name.startswith('_'):
                    func_suggestions = self._analyze_function_for_edge_cases(node, content)
                    if func_suggestions:
                        suggestions.extend([f"{node.name}: {suggestion}" for suggestion in func_suggestions])
        
        except Exception as e:
            print(f"Warnung: Fehler beim Analysieren von {file_path}: {e}")
        
        return suggestions
    
    def _analyze_function_for_edge_cases(self, func_node: ast.FunctionDef, content: str) -> List[str]:
        """Analysiert eine einzelne Funktion für Edge Cases."""
        suggestions = []
        
        # Analysiere Parameter
        for arg in func_node.args.args:
            if arg.arg != 'self':
                suggestions.extend(self._suggest_edge_cases_for_param(arg.arg))
        
        # Analysiere Funktionskörper für potentielle Edge Cases
        for node in ast.walk(func_node):
            if isinstance(node, ast.Compare):
                suggestions.extend(self._suggest_comparison_edge_cases(node))
            elif isinstance(node, ast.Subscript):
                suggestions.append("Index-Zugriff: Teste leere Listen/invalide Indices")
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute) and node.func.attr in ['split', 'replace', 'strip']:
                    suggestions.append("String-Operationen: Teste leere Strings/None Werte")
        
        return list(set(suggestions))  # Duplikate entfernen
    
    def _suggest_edge_cases_for_param(self, param_name: str) -> List[str]:
        """Erstellt Edge Case Vorschläge basierend auf Parameternamen."""
        suggestions = []
        
        # String-Parameter
        if any(keyword in param_name.lower() for keyword in ['name', 'text', 'string', 'path', 'file']):
            suggestions.extend([
                "Teste leere Strings",
                "Teste None-Werte",
                "Teste sehr lange Strings",
                "Teste Strings mit Sonderzeichen"
            ])
        
        # Numerische Parameter
        if any(keyword in param_name.lower() for keyword in ['count', 'number', 'size', 'length', 'index']):
            suggestions.extend([
                "Teste negative Werte",
                "Teste Null-Werte",
                "Teste sehr große Zahlen"
            ])
        
        # Listen/Collections
        if any(keyword in param_name.lower() for keyword in ['list', 'items', 'data', 'collection']):
            suggestions.extend([
                "Teste leere Listen",
                "Teste Listen mit einem Element",
                "Teste None-Listen"
            ])
        
        return suggestions
    
    def _suggest_comparison_edge_cases(self, compare_node: ast.Compare) -> List[str]:
        """Erstellt Edge Case Vorschläge für Vergleichsoperationen."""
        suggestions = []
        
        for op in compare_node.ops:
            if isinstance(op, ast.Eq):
                suggestions.append("Gleichheitsvergleich: Teste Grenzwerte")
            elif isinstance(op, (ast.Lt, ast.LtE, ast.Gt, ast.GtE)):
                suggestions.append("Zahlenvergleich: Teste Grenzwerte und Off-by-One Fehler")
        
        return suggestions

def test_edge_case_coverage():
    """Test für Edge Case Abdeckung - informativ, kein Fehler."""
    analyzer = EdgeCaseAnalyzer(REPO_ROOT)
    suggestions = analyzer.analyze_edge_cases()
    
    if suggestions:
        print("\n💡 Edge Case Vorschläge für bessere Testabdeckung:")
        for file_path, file_suggestions in suggestions.items():
            print(f"\n📁 {file_path}:")
            for suggestion in file_suggestions[:3]:  # Zeige nur die ersten 3
                print(f"  • {suggestion}")
        print(f"\nInsgesamt {len(suggestions)} Dateien mit Edge Case Möglichkeiten analysiert.")
    else:
        print("✅ Keine offensichtlichen Edge Case Lücken gefunden.")

# ============================================================================
# 5. DOKUMENTATIONSQUALITÄT - Docstring-Analyse
# ============================================================================

class DocumentationAnalyzer:
    """Analysiert die Qualität der Dokumentation."""
    
    def __init__(self, repo_root: str, min_docstring_length: int = MIN_DOCSTRING_LENGTH):
        self.repo_root = repo_root
        self.min_docstring_length = min_docstring_length
    
    def analyze_documentation(self) -> Dict[str, List[str]]:
        """Analysiert Dokumentationsqualität im Projekt."""
        issues = {}
        
        for root, dirs, files in os.walk(self.repo_root):
            dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
            
            for file in files:
                if file.endswith('.py') and not file.startswith('test_'):
                    file_path = os.path.join(root, file)
                    file_issues = self._analyze_file_documentation(file_path)
                    if file_issues:
                        rel_path = os.path.relpath(file_path, self.repo_root)
                        issues[rel_path] = file_issues
        
        return issues
    
    def _analyze_file_documentation(self, file_path: str) -> List[str]:
        """Analysiert Dokumentation einer einzelnen Datei."""
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content, filename=file_path)
            
            # Analysiere Klassen und Funktionen
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    issue = self._check_docstring(node, 'Klasse', node.name)
                    if issue:
                        issues.append(issue)
                
                elif isinstance(node, ast.FunctionDef) and not node.name.startswith('_'):
                    issue = self._check_docstring(node, 'Funktion', node.name)
                    if issue:
                        issues.append(issue)
        
        except Exception as e:
            issues.append(f"Fehler beim Analysieren: {str(e)}")
        
        return issues
    
    def _check_docstring(self, node: ast.AST, item_type: str, name: str) -> Optional[str]:
        """Prüft Docstring-Qualität für einen AST-Knoten."""
        docstring = ast.get_docstring(node)
        
        if not docstring:
            return f"{item_type} '{name}': Kein Docstring vorhanden"
        
        if len(docstring.strip()) < self.min_docstring_length:
            return f"{item_type} '{name}': Docstring zu kurz (< {self.min_docstring_length} Zeichen)"
        
        # Prüfe auf Standard-Phrasen
        if docstring.strip().lower() in ['todo', 'fixme', 'placeholder']:
            return f"{item_type} '{name}': Placeholder-Docstring gefunden"
        
        return None

def test_documentation_quality():
    """Test für Dokumentationsqualität - informativ."""
    analyzer = DocumentationAnalyzer(REPO_ROOT)
    issues = analyzer.analyze_documentation()
    
    if issues:
        print(f"\n📖 Dokumentationsverbesserungen möglich ({len(issues)} Dateien):")
        for file_path, file_issues in issues.items():
            print(f"\n📁 {file_path}:")
            for issue in file_issues:
                print(f"  • {issue}")
        print("\n💡 Hinweis: Bessere Dokumentation verbessert die Wartbarkeit des Codes.")
    else:
        print("✅ Dokumentationsqualität ist ausreichend.")

# ============================================================================
# 6. WORKFLOW-VALIDIERUNG - Erweiterte GitHub Actions Prüfung
# ============================================================================

def test_workflow_validation():
    """Test für GitHub Workflows mit erweiterten Prüfungen."""
    workflow_dir = os.path.join(REPO_ROOT, ".github", "workflows")
    
    if not os.path.isdir(workflow_dir):
        pytest.fail("❌ Kein .github/workflows Verzeichnis gefunden!")
    
    workflow_files = [f for f in os.listdir(workflow_dir) if f.endswith(('.yml', '.yaml'))]
    
    if not workflow_files:
        pytest.fail("❌ Keine Workflow-Dateien gefunden!")
    
    issues = []
    
    for workflow_file in workflow_files:
        workflow_path = os.path.join(workflow_dir, workflow_file)
        file_issues = _analyze_workflow_file(workflow_path)
        if file_issues:
            issues.extend([f"{workflow_file}: {issue}" for issue in file_issues])
    
    if issues:
        msg = "Workflow-Probleme gefunden:\n"
        for issue in issues:
            msg += f"  - {issue}\n"
        pytest.fail(msg)
    else:
        print("✅ Alle Workflow-Dateien sind ordnungsgemäß konfiguriert.")

def _analyze_workflow_file(workflow_path: str) -> List[str]:
    """Analysiert eine einzelne Workflow-Datei."""
    issues = []
    
    try:
        with open(workflow_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Grundlegende Checks
        if "actions/checkout" not in content and "uses: checkout" not in content:
            issues.append("Fehlt checkout Action")
        
        if "run:" not in content and "run |" not in content:
            issues.append("Fehlt run Befehle")
        
        # Erweiterte Checks
        if "python" in content.lower() and "setup-python" not in content:
            issues.append("Python-Workflow ohne setup-python Action")
        
        if "test" in content.lower() and "pytest" not in content and "unittest" not in content:
            issues.append("Test-Workflow ohne erkennbares Test-Framework")
    
    except Exception as e:
        issues.append(f"Fehler beim Lesen: {str(e)}")
    
    return issues

# ============================================================================
# HILFSFUNKTIONEN UND UTILITIES
# ============================================================================

def get_project_stats() -> Dict[str, int]:
    """Sammelt grundlegende Projektstatistiken."""
    stats = {
        'python_files': 0,
        'total_functions': 0,
        'total_classes': 0,
        'total_lines': 0
    }
    
    for root, dirs, files in os.walk(REPO_ROOT):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
        
        for file in files:
            if file.endswith('.py') and not file.startswith('test_'):
                stats['python_files'] += 1
                file_path = os.path.join(root, file)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        stats['total_lines'] += len(content.split('\n'))
                    
                    tree = ast.parse(content, filename=file_path)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            stats['total_functions'] += 1
                        elif isinstance(node, ast.ClassDef):
                            stats['total_classes'] += 1
                
                except Exception:
                    continue
    
    return stats

def test_project_overview():
    """Informationstest - Zeigt Projektüberblick."""
    stats = get_project_stats()
    
    print(f"\n📊 AFMTool1 Projektstatistiken:")
    print(f"  • Python-Dateien: {stats['python_files']}")
    print(f"  • Funktionen: {stats['total_functions']}")
    print(f"  • Klassen: {stats['total_classes']}")
    print(f"  • Zeilen Code: {stats['total_lines']:,}")
    print(f"  • Durchschnitt Zeilen/Datei: {stats['total_lines'] // max(stats['python_files'], 1)}")

# ============================================================================
# Startpunkt für pytest: pytest test_quality.py -v
# ============================================================================