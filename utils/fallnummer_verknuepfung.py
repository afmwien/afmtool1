"""
AFMTool1 - Fallnummer-Gruppierung für GUI/Web-Interface
Mit 5-stelligen Hash-UUIDs als Fallback für leere Fallnummern
"""
import hashlib

def generate_hash_uuid(case):
    """5-stelligen Hash aus erfassung-Zeitstempel generieren"""
    for ts in case.get("zeitstempel", []):
        if ts.startswith("erfassung:"):
            timestamp_part = ts.replace("erfassung:", "")
            hash_obj = hashlib.md5(timestamp_part.encode('utf-8'))
            short_hash = hash_obj.hexdigest()[:5].upper()
            return short_hash
    return "ERROR"

def ensure_fallnummer(case):
    """
    Stellt sicher, dass jeder Case eine gültige Fallnummer hat
    Fallback: Hash-UUID als Fallnummer wenn leer/None
    """
    fallnummer = case.get("fallnummer", "")
    if fallnummer is None:
        fallnummer = ""
    else:
        fallnummer = str(fallnummer).strip()
    
    if not fallnummer or fallnummer in ["", "LEER", "NONE", "NULL"]:
        hash_uuid = generate_hash_uuid(case)
        case["fallnummer"] = f"AUTO-{hash_uuid}"
        return f"AUTO-{hash_uuid}"
    return fallnummer

def find_fallnummer_groups(cases):
    """
    Gruppiert Cases nach Fallnummer mit Hash-UUIDs
    Auto-Fallnummer für leere Cases
    Returns: {"exakte_gruppen": {fallnummer: [hash_uuids]}}
    """
    exact_groups = {}
    for case in cases:
        if isinstance(case, dict):
            fallnummer = ensure_fallnummer(case)
        else:
            continue
        if fallnummer not in exact_groups:
            exact_groups[fallnummer] = []
        hash_uuid = generate_hash_uuid(case)
        exact_groups[fallnummer].append(hash_uuid)
    
    return {
        "exakte_gruppen": exact_groups
    }

def get_grouped_cases_by_fallnummer(target_fallnummer, cases):
    """
    Gibt alle Cases mit der gleichen Fallnummer zurück
    """
    related_cases = []
    
    for case in cases:
        if isinstance(case, dict) and case.get("fallnummer") == target_fallnummer:
            related_cases.append(case)
    
    return related_cases

def get_case_summary(cases):
    """
    Erstellt Zusammenfassung aller Cases mit Hash-UUIDs
    Garantiert gültige Fallnummern durch Auto-Fallback
    """
    summary = []
    for case in cases:
        if isinstance(case, dict):
            fallnummer = ensure_fallnummer(case)
            summary.append({
                "uuid": generate_hash_uuid(case),
                "fallnummer": fallnummer,
                "quelle": case.get("quelle", "KEINE_QUELLE"),
                "zeitstempel_count": len(case.get("zeitstempel", []))
            })
    return summary

if __name__ == "__main__":
    # Test mit leeren Fallnummern
    import json
    from pathlib import Path
    
    # Cases aus JSON laden
    json_path = Path(__file__).parent.parent / "data" / "cases.json"
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            cases = data.get('cases', [])
        print(f"✅ {len(cases)} Cases aus cases.json geladen")
    except Exception as e:
        print(f"❌ Fehler beim Laden: {e}")
        cases = []
    
    # Test-Cases mit leeren Fallnummern hinzufügen
    test_cases = [
        {"fallnummer": "", "zeitstempel": ["erfassung:2025-07-24T12:00:00.000000:test-empty-1"], "quelle": "Test ohne Fallnummer"},
        {"fallnummer": None, "zeitstempel": ["erfassung:2025-07-24T12:01:00.000000:test-none-2"], "quelle": "Test mit None"},
        {"zeitstempel": ["erfassung:2025-07-24T12:02:00.000000:test-missing-3"], "quelle": "Test ohne fallnummer Feld"}
    ]
    
    all_cases = cases + test_cases
    
    print(f"\n=== Fallnummer-Fallback Test ({len(all_cases)} Cases) ===")
    groups = find_fallnummer_groups(all_cases)
    
    print(f"📊 {len(groups['exakte_gruppen'])} Fallnummer-Gruppen:")
    for fallnummer, hash_uuids in groups["exakte_gruppen"].items():
        if fallnummer.startswith("AUTO-"):
            print(f"  🔄 {fallnummer}: {len(hash_uuids)} Cases (Auto-generiert)")
        else:
            print(f"  ✅ {fallnummer}: {len(hash_uuids)} Cases")
    
    print(f"\n📋 Letzte 3 Cases (inkl. Auto-Fallnummern):")
    summary = get_case_summary(all_cases[-3:])
    for case_info in summary:
        marker = "🔄" if case_info['fallnummer'].startswith("AUTO-") else "✅"
        print(f"  {marker} {case_info['uuid']}: {case_info['fallnummer']}")