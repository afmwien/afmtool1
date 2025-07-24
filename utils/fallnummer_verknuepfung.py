"""
Fallnummer-basierte Verknüpfung für AFMTool1
Automatische Erkennung von verwandten Fällen über Fallnummer-Patterns
"""
import re
from datetime import datetime

def find_cross_references(cases):
    """
    Findet Verknüpfungen zwischen Cases basierend auf Fallnummer-Patterns
    
    Args:
        cases (list): Liste der Cases aus cases.json
        
    Returns:
        dict: Verknüpfungsgruppen nach verschiedenen Kriterien
    """
    
    # 1. Präfix-basierte Gruppierung (FA-, GB-, FB-, etc.)
    prefix_groups = {}
    for case in cases:
        if isinstance(case, dict):
            fallnummer = case.get("fallnummer", "")
        else:
            continue
        if "-" in fallnummer:
            prefix = fallnummer.split("-")[0]  # z.B. "FA" aus "FA-2025-001"
            if prefix not in prefix_groups:
                prefix_groups[prefix] = []
            prefix_groups[prefix].append(fallnummer)
    
    # 2. Jahr-basierte Gruppierung (2025)
    year_groups = {}
    for case in cases:
        if isinstance(case, dict):
            fallnummer = case.get("fallnummer", "")
        else:
            continue
        year_match = re.search(r'(\d{4})', fallnummer)
        if year_match:
            year = year_match.group(1)
            if year not in year_groups:
                year_groups[year] = []
            year_groups[year].append(fallnummer)
    
    # 3. Sequenz-basierte Verwandtschaft (TST-2025-001, TST-2025-002)
    sequence_groups = {}
    for case in cases:
        if isinstance(case, dict):
            fallnummer = case.get("fallnummer", "")
        else:
            continue
        # Pattern: PREFIX-JAHR-XXX
        match = re.match(r'([A-Z]+)-(\d{4})-(\d+)', fallnummer)
        if match:
            prefix, year, number = match.groups()
            base_pattern = f"{prefix}-{year}"
            if base_pattern not in sequence_groups:
                sequence_groups[base_pattern] = []
            sequence_groups[base_pattern].append(fallnummer)
    
    return {
        "praefixe": prefix_groups,
        "jahre": year_groups, 
        "sequenzen": sequence_groups
    }

def get_related_cases_by_fallnummer(target_fallnummer, cases):
    """
    Findet alle verwandten Cases für eine bestimmte Fallnummer
    
    Args:
        target_fallnummer (str): Ziel-Fallnummer
        cases (list): Alle Cases
        
    Returns:
        dict: Verwandte Cases nach Beziehungstyp
    """
    cross_refs = find_cross_references(cases)
    related = {
        "gleicher_typ": [],      # Gleicher Präfix
        "gleiches_jahr": [],     # Gleiches Jahr
        "gleiche_serie": []      # Gleiche Sequenz
    }
    
    # Präfix-Verwandtschaft
    if "-" in target_fallnummer:
        target_prefix = target_fallnummer.split("-")[0]
        related["gleicher_typ"] = cross_refs["praefixe"].get(target_prefix, [])
        related["gleicher_typ"] = [fn for fn in related["gleicher_typ"] if fn != target_fallnummer]
    
    # Jahr-Verwandtschaft
    year_match = re.search(r'(\d{4})', target_fallnummer)
    if year_match:
        target_year = year_match.group(1)
        related["gleiches_jahr"] = cross_refs["jahre"].get(target_year, [])
        related["gleiches_jahr"] = [fn for fn in related["gleiches_jahr"] if fn != target_fallnummer]
    
    # Sequenz-Verwandtschaft
    match = re.match(r'([A-Z]+)-(\d{4})-(\d+)', target_fallnummer)
    if match:
        prefix, year, number = match.groups()
        base_pattern = f"{prefix}-{year}"
        related["gleiche_serie"] = cross_refs["sequenzen"].get(base_pattern, [])
        related["gleiche_serie"] = [fn for fn in related["gleiche_serie"] if fn != target_fallnummer]
    
    return related

# Beispiel-Implementierung für DataService
def add_to_data_service():
    """
    Integration in die DataService-Klasse
    """
    code_example = '''
    def get_related_cases(self, case_index):
        """Verwandte Cases über Fallnummer finden"""
        cases = self.get_cases()
        if case_index >= len(cases):
            return {}
            
        current_case = cases[case_index]
        current_fallnummer = current_case.get("fallnummer", "")
        
        if not current_fallnummer:
            return {}
        
        related = get_related_cases_by_fallnummer(current_fallnummer, cases)
        
        # Fallnummern zu Case-Indices umwandeln
        result = {}
        for relation_type, fallnummern in related.items():
            result[relation_type] = []
            for fallnummer in fallnummern:
                for i, case in enumerate(cases):
                    if case.get("fallnummer") == fallnummer:
                        result[relation_type].append({
                            "index": i,
                            "fallnummer": fallnummer,
                            "quelle": case.get("quelle", ""),
                            "status": self.get_case_status(case)
                        })
        
        return result
    '''
    return code_example

if __name__ == "__main__":
    # Test mit aktuellen Cases
    test_cases = [
        {"fallnummer": "FA-2025-001"},
        {"fallnummer": "GB-2025-007"}, 
        {"fallnummer": "FB-2025-123"},
        {"fallnummer": "TST-2025-001"},
        {"fallnummer": "TST-2025-002"},
        {"fallnummer": "WEB-2025-003"}
    ]
    
    print("🔍 Cross-Reference Analyse:")
    cross_refs = find_cross_references(test_cases)
    
    print("\n📊 Präfix-Gruppen:")
    for prefix, gruppe in cross_refs["praefixe"].items():
        print(f"  {prefix}: {gruppe}")
    
    print("\n📅 Jahr-Gruppen:")
    for jahr, gruppe in cross_refs["jahre"].items():
        print(f"  {jahr}: {len(gruppe)} Cases")
    
    print("\n🔗 Sequenz-Gruppen:")
    for sequenz, gruppe in cross_refs["sequenzen"].items():
        if len(gruppe) > 1:  # Nur Gruppen mit mehreren Cases
            print(f"  {sequenz}: {gruppe}")
    
    print("\n🎯 Verwandte Cases für TST-2025-001:")
    related = get_related_cases_by_fallnummer("TST-2025-001", test_cases)
    for typ, cases in related.items():
        if cases:
            print(f"  {typ}: {cases}")
