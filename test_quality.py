"""
Testskript für AFMTool1
Punkt 1: Suche nach überflüssigem/nicht mehr gebrauchtem Code (aktiv)
Punkt 2: Fehlende Verlinkungen
Punkt 3: Workflow-Überprüfung
Punkt 4: Kompatibilität für Internetanwendung
"""

import os
import ast
import pytest

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
    Prüft, ob das Projekt von lokalen Dateipfaden und IO unabhängig ist.
    Gibt Hinweise auf Bereiche, die für Webanwendung angepasst werden müssen.
    """
    # Beispiel: Suche nach direkten open()-Aufrufen außerhalb von Utils/DB
    issues = []
    for root, _, files in os.walk(REPO_ROOT):
        for fname in files:
            if fname.endswith(".py"):
                fpath = os.path.join(root, fname)
                with open(fpath, encoding="utf-8") as f:
                    content = f.read()
                    if "open(" in content and "utils" not in fpath:
                        issues.append(fpath)
    assert not issues, f"Dateioperationen gefunden, die für Web-Kompatibilität problematisch sind: {issues}"

# -------------------
# Zum Starten: pytest test_quality.py