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
    # Hier würdest du z.B. checken, ob zentrale Funktionen in main.py,
    # main_gui.py und gui/main_window.py wirklich genutzt werden.
    # Das kann durch eine Kombination aus ast und gezielten Checks erfolgen.
    assert True  # Platzhalter für echten Test

# ----------- Punkt 3: Workflow überprüfen -----------

def test_workflow_files():
    """
    Prüft, ob .github/workflows existiert und mindestens ein Workflow definiert ist.
    """
    workflow_dir = os.path.join(REPO_ROOT, ".github", "workflows")
    assert os.path.isdir(workflow_dir), "Kein Workflow-Verzeichnis gefunden!"
    files = [f for f in os.listdir(workflow_dir) if f.endswith(".yml") or f.endswith(".yaml")]
    assert files, "Keine Workflow-Dateien gefunden!"
    # Optional: Inhalte der Workflows auf wichtige Schritte prüfen

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