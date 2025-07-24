"""
AFMTool1 - Umfassende Code-Qualitätsprüfung für GitHub Actions
Erweiterte Testabdeckung für Continuous Integration

Tests:
1. Überflüssiger/nicht gebrauchter Code
2. Fehlende Verlinkungen 
3. Workflow-Überprüfung
4. Web-Kompatibilität
5. Code-Style & Best Practices
6. Sicherheitsprüfungen
7. Error-Handling
8. Import-Struktur
9. Dokumentation
10. Performance & Dateigröße
11. JSON-Validierung
12. GitHub Actions Integration
"""

import os
import ast
import json

# Pytest optional - für GitHub Actions
try:
    import pytest
    PYTEST_AVAILABLE = True
except ImportError:
    PYTEST_AVAILABLE = False
    # Mock pytest.fail für lokale Ausführung
    class MockPytest:
        @staticmethod
        def fail(msg):
            raise AssertionError(msg)
    pytest = MockPytest()

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))

# ----------- Punkt 1: Überflüssiger oder nicht mehr gebrauchter Code -----------

def find_unused_functions(directory):
    unused = []
    for root, _, files in os.walk(directory):
        for fname in files:
            if fname.endswith(".py") and "test_" not in fname and fname != "test_quality.py":
                path = os.path.join(root, fname)
                with open(path, encoding="utf-8") as f:
                    try:
                        tree = ast.parse(f.read(), filename=fname)
                    except Exception:
                        continue
                func_defs = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
                for func in func_defs:
                    if func.name.startswith("__"):
                        continue
                    used = False
                    with open(path, encoding="utf-8") as f:
                        code = f.read()
                        # Suche nach Funktionsaufrufen im eigenen File
                        if f"{func.name}(" in code and code.index(f"{func.name}(" ) != code.index(f"def {func.name}(" ):
                            used = True
                    if not used:
                        unused.append((fname, func.name))
    return unused

def test_no_unused_functions():
    unused = find_unused_functions(REPO_ROOT)
    if unused:
        msg = "Nicht genutzte Funktionen gefunden:\n"
        for fname, func in unused:
            msg += f"  - {fname}: {func}\n"
        pytest.fail(msg)
    else:
        print("Keine überflüssigen Funktionen gefunden.")

# ----------- Punkt 2: Fehlende Verlinkungen -----------

def test_missing_links():
    """
    Testet, ob alle wichtigen Funktionsaufrufe, Importe und GUI-Callbacks vorhanden sind.
    """
    # Zentrale Dateien definieren, die geprüft werden sollen
    central_files = [
        "main.py",
        "main_gui.py", 
        "gui/main_window.py"
    ]
    
    # Funktionen, die als Event-Handler oder Public API legitim ungenutzt sein können
    excluded_patterns = [
        "on_",       # Event handler
        "_view",     # View methods
        "show_",     # Show methods
        "generate_", # Generator methods
        "quit_",     # Exit methods
    ]
    
    missing_links = []
    
    for central_file in central_files:
        file_path = os.path.join(REPO_ROOT, central_file)
        if not os.path.exists(file_path):
            continue
            
        # Funktionen in der zentralen Datei finden
        with open(file_path, encoding="utf-8") as f:
            try:
                tree = ast.parse(f.read(), filename=central_file)
            except Exception:
                continue
                
        # Funktionsdefinitionen und Klassenmethoden extrahieren
        functions_and_methods = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if not node.name.startswith("__"):  # Private Methoden ignorieren
                    functions_and_methods.append(node.name)
            elif isinstance(node, ast.ClassDef):
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and not item.name.startswith("__"):
                        functions_and_methods.append(f"{node.name}.{item.name}")
        
        # Duplikate entfernen
        functions_and_methods = list(set(functions_and_methods))
        
        # Prüfen, ob diese Funktionen irgendwo aufgerufen werden
        for func_name in functions_and_methods:
            # Überspringe ausgeschlossene Patterns (Event Handler, etc.)
            should_exclude = False
            method_name = func_name.split('.')[-1]  # Letzter Teil für Klassenmethoden
            for pattern in excluded_patterns:
                if method_name.startswith(pattern):
                    should_exclude = True
                    break
            
            if should_exclude:
                continue
                
            if not _is_function_called(func_name, central_file):
                missing_links.append(f"{central_file}: {func_name}")
    
    if missing_links:
        msg = "Nicht verlinkte zentrale Funktionen gefunden:\n"
        for link in missing_links:
            msg += f"  - {link}\n"
        pytest.fail(msg)
    else:
        print("Alle kritischen zentralen Funktionen sind ordnungsgemäß verlinkt.")

def _is_function_called(func_name, source_file):
    """Hilfsfunktion: Prüft, ob eine Funktion irgendwo im Projekt aufgerufen wird."""
    # Einfache Namensextraktionslogik für Klassenmethoden
    if "." in func_name:
        class_name, method_name = func_name.split(".", 1)
        search_patterns = [
            f"{method_name}(",
            f".{method_name}(",
            f"self.{method_name}(",
            f"parent.{method_name}(",
            f"command={method_name}",
            f"command=self.{method_name}",
            f'"{method_name}"',  # Event handler names
            f"'{method_name}'"   # Event handler names
        ]
    else:
        search_patterns = [
            f"{func_name}(",
            f"command={func_name}",
            f'"{func_name}"',
            f"'{func_name}'"
        ]
    
    # Durchsuche alle Python-Dateien im Projekt (inklusive Komponenten)
    for root, _, files in os.walk(REPO_ROOT):
        for fname in files:
            if fname.endswith(".py") and not fname.startswith("test_"):
                fpath = os.path.join(root, fname)
                # Überspringe .venv
                if ".venv" in fpath:
                    continue
                    
                try:
                    with open(fpath, encoding="utf-8") as f:
                        content = f.read()
                        
                    for pattern in search_patterns:
                        if pattern in content:
                            # Wenn in derselben Datei gefunden, sicherstellen dass es nicht nur die Definition ist
                            if os.path.basename(fpath) == os.path.basename(source_file):
                                # Prüfe, ob es Aufrufe außerhalb der Funktionsdefinition gibt
                                lines = content.split('\n')
                                definition_found = False
                                call_found = False
                                
                                for line in lines:
                                    # Skip definition lines
                                    if f"def {func_name.split('.')[-1]}(" in line:
                                        definition_found = True
                                        continue
                                    # Look for calls
                                    if pattern in line and not line.strip().startswith('#'):
                                        call_found = True
                                        break
                                
                                if call_found:
                                    return True
                            else:
                                # In anderer Datei gefunden - das ist ein Aufruf
                                return True
                                
                except Exception:
                    continue
    
    return False

# ----------- Punkt 3: Workflow überprüfen -----------

def test_workflow_files():
    """
    Prüft, ob .github/workflows existiert und mindestens ein Workflow definiert ist.
    Überprüft auch, ob Workflows die erforderlichen Schritte 'checkout' und 'run' enthalten.
    """
    workflow_dir = os.path.join(REPO_ROOT, ".github", "workflows")
    assert os.path.isdir(workflow_dir), "Kein Workflow-Verzeichnis gefunden!"
    
    files = [f for f in os.listdir(workflow_dir) if f.endswith(".yml") or f.endswith(".yaml")]
    assert files, "Keine Workflow-Dateien gefunden!"
    
    # Prüfe Workflow-Inhalte auf wichtige Schritte
    missing_steps = []
    
    for workflow_file in files:
        workflow_path = os.path.join(workflow_dir, workflow_file)
        try:
            with open(workflow_path, encoding="utf-8") as f:
                content = f.read()
                
            # Prüfe auf checkout und run Schritte
            has_checkout = _check_workflow_step(content, "checkout")
            has_run = _check_workflow_step(content, "run")
            
            if not has_checkout:
                missing_steps.append(f"{workflow_file}: fehlt 'checkout' Schritt")
            if not has_run:
                missing_steps.append(f"{workflow_file}: fehlt 'run' Schritt")
                
        except Exception as e:
            missing_steps.append(f"{workflow_file}: Fehler beim Lesen - {str(e)}")
    
    if missing_steps:
        msg = "Workflow-Dateien mit fehlenden Schritten:\n"
        for step in missing_steps:
            msg += f"  - {step}\n"
        pytest.fail(msg)
    else:
        print("Alle Workflow-Dateien enthalten die erforderlichen Schritte 'checkout' und 'run'.")

def _check_workflow_step(content, step_type):
    """Hilfsfunktion: Prüft ob ein Workflow-Schritt vorhanden ist."""
    if step_type == "checkout":
        # Prüfe auf checkout Action
        return "actions/checkout" in content or "uses: checkout" in content
    elif step_type == "run":
        # Prüfe auf run Kommandos
        return "run:" in content or "run |" in content
    return False

# ----------- Punkt 4: Kompatibilität für Internetanwendung -----------

def test_web_compatibility():
    """
    Prüft Web-Kompatibilität: Keine GUI-Abhängigkeiten in core modules
    """
    web_incompatible = []
    core_modules = ["utils/", "data/", "services/"]
    
    for module_path in core_modules:
        full_path = os.path.join(REPO_ROOT, module_path)
        if not os.path.exists(full_path):
            continue
            
        for root, _, files in os.walk(full_path):
            for fname in files:
                if fname.endswith(".py"):
                    fpath = os.path.join(root, fname)
                    with open(fpath, encoding="utf-8") as f:
                        content = f.read()
                    
                    # GUI-Abhängigkeiten prüfen
                    gui_imports = ["tkinter", "PyQt", "wx", "kivy", "pygame"]
                    for gui_lib in gui_imports:
                        if f"import {gui_lib}" in content or f"from {gui_lib}" in content:
                            web_incompatible.append(f"{fname}: {gui_lib} Import")
    
    if web_incompatible:
        msg = "Web-inkompatible GUI-Abhängigkeiten gefunden:\n"
        for issue in web_incompatible:
            msg += f"  - {issue}\n"
        pytest.fail(msg)
    else:
        print("Core-Module sind web-kompatibel.")

# ----------- Punkt 5: Code-Qualität & Best Practices -----------

def test_code_style():
    """Prüft Python Code-Style Konventionen"""
    style_issues = []
    
    for root, _, files in os.walk(REPO_ROOT):
        if ".venv" in root or "__pycache__" in root:
            continue
            
        for fname in files:
            if fname.endswith(".py"):
                fpath = os.path.join(root, fname)
                try:
                    with open(fpath, encoding="utf-8") as f:
                        lines = f.readlines()
                    
                    for i, line in enumerate(lines, 1):
                        # Zeilen über 120 Zeichen
                        if len(line.rstrip()) > 120:
                            style_issues.append(f"{fname}:{i} - Zeile zu lang ({len(line.rstrip())} Zeichen)")
                        
                        # Trailing Whitespace
                        if line.endswith(" \n") or line.endswith("\t\n"):
                            style_issues.append(f"{fname}:{i} - Trailing Whitespace")
                        
                        # TODO/FIXME/HACK Kommentare
                        if any(marker in line.upper() for marker in ["TODO", "FIXME", "HACK", "XXX"]):
                            style_issues.append(f"{fname}:{i} - Unerledigter Marker: {line.strip()}")
                            
                except Exception:
                    continue
    
    if len(style_issues) > 10:  # Nur kritische Anzahl melden
        msg = f"Code-Style Probleme gefunden ({len(style_issues)} total, erste 10):\n"
        for issue in style_issues[:10]:
            msg += f"  - {issue}\n"
        pytest.fail(msg)
    else:
        print(f"Code-Style OK ({len(style_issues)} kleinere Probleme)")

def test_security_issues():
    """Prüft auf grundlegende Sicherheitsprobleme"""
    security_issues = []
    
    dangerous_patterns = [
        ("eval(", "Dangerous eval() usage"),
        ("exec(", "Dangerous exec() usage"),
        ("os.system(", "Dangerous os.system() usage"),
        ("shell=True", "Subprocess with shell=True"),
        ("input(", "Raw input() usage"),
        ("pickle.load", "Unsafe pickle.load"),
        ("yaml.load(", "Unsafe yaml.load without Loader"),
    ]
    
    for root, _, files in os.walk(REPO_ROOT):
        if ".venv" in root:
            continue
            
        for fname in files:
            if fname.endswith(".py"):
                fpath = os.path.join(root, fname)
                try:
                    with open(fpath, encoding="utf-8") as f:
                        content = f.read()
                    
                    for pattern, description in dangerous_patterns:
                        if pattern in content:
                            security_issues.append(f"{fname}: {description}")
                            
                except Exception:
                    continue
    
    if security_issues:
        msg = "Potentielle Sicherheitsprobleme gefunden:\n"
        for issue in security_issues:
            msg += f"  - {issue}\n"
        pytest.fail(msg)
    else:
        print("Keine offensichtlichen Sicherheitsprobleme gefunden.")

def test_error_handling():
    """Prüft auf ordnungsgemäße Error-Behandlung"""
    error_issues = []
    
    for root, _, files in os.walk(REPO_ROOT):
        if ".venv" in root:
            continue
            
        for fname in files:
            if fname.endswith(".py"):
                fpath = os.path.join(root, fname)
                try:
                    with open(fpath, encoding="utf-8") as f:
                        content = f.read()
                    
                    # Bare except clauses
                    if "except:" in content and "except Exception:" not in content:
                        error_issues.append(f"{fname}: Bare except clause gefunden")
                    
                    # Print statements für Error handling
                    lines = content.split('\n')
                    for i, line in enumerate(lines, 1):
                        if "except" in line and i < len(lines):
                            next_lines = lines[i:i+3]
                            if any("print(" in l for l in next_lines):
                                error_issues.append(f"{fname}:{i} - Print in exception handler")
                                
                except Exception:
                    continue
    
    if error_issues:
        msg = "Error-Handling Probleme gefunden:\n"
        for issue in error_issues:
            msg += f"  - {issue}\n"
        print(f"Warning: {msg}")  # Warning statt Fail
    else:
        print("Error-Handling sieht ordentlich aus.")

# ----------- Punkt 6: Dependency & Import Analyse -----------

def test_import_structure():
    """Prüft Import-Struktur und zirkuläre Abhängigkeiten"""
    import_issues = []
    all_imports = {}
    
    for root, _, files in os.walk(REPO_ROOT):
        if ".venv" in root or "__pycache__" in root:
            continue
            
        for fname in files:
            if fname.endswith(".py"):
                fpath = os.path.join(root, fname)
                rel_path = os.path.relpath(fpath, REPO_ROOT).replace("\\", "/")
                
                try:
                    with open(fpath, encoding="utf-8") as f:
                        tree = ast.parse(f.read())
                    
                    imports = []
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                imports.append(alias.name)
                        elif isinstance(node, ast.ImportFrom):
                            if node.module:
                                imports.append(node.module)
                    
                    all_imports[rel_path] = imports
                    
                    # Relative imports prüfen
                    for imp in imports:
                        if imp.startswith("."):
                            import_issues.append(f"{fname}: Relative import {imp}")
                            
                except Exception:
                    continue
    
    # Zirkuläre Abhängigkeiten einfach prüfen
    for file_path, imports in all_imports.items():
        module_name = file_path.replace("/", ".").replace(".py", "")
        for imp in imports:
            if imp in all_imports and module_name in all_imports[imp]:
                import_issues.append(f"Zirkuläre Abhängigkeit: {file_path} <-> {imp}")
    
    if import_issues:
        msg = "Import-Struktur Probleme gefunden:\n"
        for issue in import_issues[:5]:  # Nur erste 5
            msg += f"  - {issue}\n"
        print(f"Warning: {msg}")
    else:
        print("Import-Struktur sieht sauber aus.")

def test_documentation():
    """Prüft Dokumentations-Vollständigkeit"""
    doc_issues = []
    
    for root, _, files in os.walk(REPO_ROOT):
        if ".venv" in root or "__pycache__" in root:
            continue
            
        for fname in files:
            if fname.endswith(".py") and not fname.startswith("test_"):
                fpath = os.path.join(root, fname)
                try:
                    with open(fpath, encoding="utf-8") as f:
                        tree = ast.parse(f.read())
                    
                    # Prüfe Modul-Docstring
                    if not ast.get_docstring(tree):
                        doc_issues.append(f"{fname}: Fehlt Modul-Docstring")
                    
                    # Prüfe Funktions-Docstrings
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            if not node.name.startswith("_") and not ast.get_docstring(node):
                                doc_issues.append(f"{fname}: {node.name}() fehlt Docstring")
                                
                except Exception:
                    continue
    
    if len(doc_issues) > 15:  # Nur bei vielen fehlenden Docs warnen
        msg = f"Dokumentations-Probleme gefunden ({len(doc_issues)} total, erste 10):\n"
        for issue in doc_issues[:10]:
            msg += f"  - {issue}\n"
        print(f"Warning: {msg}")
    else:
        print(f"Dokumentation weitgehend vollständig ({len(doc_issues)} kleinere Lücken)")

# ----------- Punkt 7: Performance & Resource Tests -----------

def test_file_sizes():
    """Prüft auf übermäßig große Dateien"""
    large_files = []
    
    for root, _, files in os.walk(REPO_ROOT):
        if ".venv" in root or "__pycache__" in root:
            continue
            
        for fname in files:
            if fname.endswith((".py", ".json", ".md")):
                fpath = os.path.join(root, fname)
                size = os.path.getsize(fpath)
                
                # Python files über 5KB, JSON über 50KB prüfen
                if fname.endswith(".py") and size > 5000:
                    large_files.append(f"{fname}: {size//1024}KB (Python-Datei)")
                elif fname.endswith(".json") and size > 50000:
                    large_files.append(f"{fname}: {size//1024}KB (JSON-Datei)")
                elif fname.endswith(".md") and size > 10000:
                    large_files.append(f"{fname}: {size//1024}KB (Markdown-Datei)")
    
    if large_files:
        msg = "Große Dateien gefunden (könnten aufgeteilt werden):\n"
        for file_info in large_files:
            msg += f"  - {file_info}\n"
        print(f"Info: {msg}")
    else:
        print("Dateigrößen sind angemessen.")

def test_json_validity():
    """Prüft JSON-Dateien auf Gültigkeit"""
    json_issues = []
    
    for root, _, files in os.walk(REPO_ROOT):
        for fname in files:
            if fname.endswith(".json"):
                fpath = os.path.join(root, fname)
                try:
                    with open(fpath, encoding="utf-8") as f:
                        json.load(f)
                except json.JSONDecodeError as e:
                    json_issues.append(f"{fname}: {str(e)}")
                except Exception as e:
                    json_issues.append(f"{fname}: {str(e)}")
    
    if json_issues:
        msg = "JSON-Validierungsfehler:\n"
        for issue in json_issues:
            msg += f"  - {issue}\n"
        pytest.fail(msg)
    else:
        print("Alle JSON-Dateien sind gültig.")

# ----------- GitHub Actions Integration -----------

def test_github_actions_completeness():
    """Erweiterte GitHub Actions Validierung"""
    workflow_dir = os.path.join(REPO_ROOT, ".github", "workflows")
    
    if not os.path.exists(workflow_dir):
        pytest.fail("GitHub Actions Workflow-Verzeichnis fehlt!")
    
    workflow_files = [f for f in os.listdir(workflow_dir) 
                     if f.endswith(('.yml', '.yaml'))]
    
    if not workflow_files:
        pytest.fail("Keine GitHub Workflow-Dateien gefunden!")
    
    required_workflows = ["ci.yml", "test.yml", "quality.yml"]
    missing_workflows = []
    
    for required in required_workflows:
        if required not in workflow_files:
            # Prüfe alternative Namen
            alternatives = [f for f in workflow_files if required.split('.')[0] in f]
            if not alternatives:
                missing_workflows.append(required)
    
    if missing_workflows:
        msg = f"Empfohlene Workflows fehlen: {', '.join(missing_workflows)}\n"
        msg += "Erstelle mindestens: ci.yml (für Tests), quality.yml (für dieses Modul)"
        print(f"Warning: {msg}")
    else:
        print("GitHub Actions Workflows sind vollständig.")

# ----------- Test Execution Helper -----------

def run_all_quality_tests():
    """Führt alle Qualitätstests aus und sammelt Ergebnisse"""
    import json
    results = {
        "timestamp": pytest.current_time if hasattr(pytest, 'current_time') else "unknown",
        "tests": {}
    }
    
    test_functions = [
        ("unused_functions", test_no_unused_functions),
        ("missing_links", test_missing_links), 
        ("workflow_files", test_workflow_files),
        ("web_compatibility", test_web_compatibility),
        ("code_style", test_code_style),
        ("security_issues", test_security_issues),
        ("error_handling", test_error_handling),
        ("import_structure", test_import_structure),
        ("documentation", test_documentation),
        ("file_sizes", test_file_sizes),
        ("json_validity", test_json_validity),
        ("github_actions", test_github_actions_completeness)
    ]
    
    for test_name, test_func in test_functions:
        try:
            test_func()
            results["tests"][test_name] = {"status": "PASSED", "message": "OK"}
        except Exception as e:
            results["tests"][test_name] = {"status": "FAILED", "message": str(e)}
    
    # Ergebnisse speichern
    results_file = os.path.join(REPO_ROOT, "quality_report.json")
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"Qualitätsbericht gespeichert: {results_file}")
    return results

# Zum Starten: pytest test_quality.py -v
# Für alle Tests: python test_quality.py (direkt ausführen)

if __name__ == "__main__":
    import json
    print("🔍 AFMTool1 - Umfassende Code-Qualitätsprüfung")
    print("=" * 50)
    
    results = run_all_quality_tests()
    
    # Zusammenfassung
    passed = sum(1 for test in results["tests"].values() if test["status"] == "PASSED")
    failed = sum(1 for test in results["tests"].values() if test["status"] == "FAILED")
    
    print(f"\n📊 Zusammenfassung: {passed} erfolgreich, {failed} fehlgeschlagen")
    
    if failed > 0:
        print("\n❌ Fehlgeschlagene Tests:")
        for test_name, result in results["tests"].items():
            if result["status"] == "FAILED":
                print(f"  - {test_name}: {result['message'][:100]}...")
    
    print(f"\n✅ Vollständiger Bericht: quality_report.json")