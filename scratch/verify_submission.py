"""
scratch/verify_submission.py
Automated submission auditor verifying:
1. Zero DUPLICATE or MISSING FIELDS flags in 02_QUESTIONS, 02b_FIXES, 02c_PAGES_CITATIONS.
2. All 7 minimum gates in 04_SELF_CHECK evaluate to MET.
3. All 4 Exceptional Requirement rows (B17:B20) are populated with valid evidence paths.
4. Zero secrets, API keys, or raw tokens exist in tracked git files.
"""

import os
import subprocess
import openpyxl

def audit_workbook(wb_path: str):
    wb = openpyxl.load_workbook(wb_path, data_only=False)
    print("=" * 70)
    print("  EXCEL WORKBOOK SUBMISSION AUDIT REPORT")
    print("=" * 70)
    print(f"[*] Auditing workbook at: {wb_path}\n")

    # 1. TAB 02_QUESTIONS
    ws2 = wb["02_QUESTIONS"]
    questions_b = []
    missing_fields_q = []
    for r in range(5, 305):
        qid = ws2.cell(row=r, column=1).value
        qtext = ws2.cell(row=r, column=2).value
        if not qid:
            continue
        questions_b.append((qid, qtext))

        # Check required columns per formula:
        # B(2), C(3), D(4), E(5), F(6), G(7), H(8), J(10), K(11), L(12), M(13), O(15), P(16), R(18)
        req_cols = [2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 15, 16, 18]
        empty_cols = [c for c in req_cols if not ws2.cell(row=r, column=c).value]
        if empty_cols:
            missing_fields_q.append((qid, empty_cols))

    q_texts = [q[1].lower().strip() for q in questions_b if q[1]]
    dupes_q = set([x for x in q_texts if q_texts.count(x) > 1])

    print(f"[*] 02_QUESTIONS Total Populated: {len(questions_b)} rows")
    print(f"    - Duplicates detected: {len(dupes_q)}")
    print(f"    - Missing field rows: {len(missing_fields_q)}")
    assert len(questions_b) == 300, f"Expected 300 questions, got {len(questions_b)}"
    assert len(dupes_q) == 0, f"Found duplicate questions: {dupes_q}"
    assert len(missing_fields_q) == 0, f"Found missing fields in questions: {missing_fields_q[:5]}"
    print("    [✓] PASS: 02_QUESTIONS has ZERO duplicates and ZERO missing fields.")

    # 2. TAB 02b_FIXES
    ws_fixes = wb["02b_FIXES"]
    fixes_a = []
    missing_fields_f = []
    for r in range(5, 25):
        fix_id = ws_fixes.cell(row=r, column=1).value
        if not fix_id:
            continue
        fixes_a.append(fix_id)
        # Required: B(2), C(3), D(4), E(5), F(6), G(7), H(8), I(9)
        req_cols = [2, 3, 4, 5, 6, 7, 8, 9]
        empty_cols = [c for c in req_cols if not ws_fixes.cell(row=r, column=c).value]
        if empty_cols:
            missing_fields_f.append((fix_id, empty_cols))

    dupes_f = set([x for x in fixes_a if fixes_a.count(x) > 1])
    print(f"\n[*] 02b_FIXES Total Populated: {len(fixes_a)} fixes")
    print(f"    - Duplicates detected: {len(dupes_f)}")
    print(f"    - Missing field rows: {len(missing_fields_f)}")
    assert len(fixes_a) == 20, f"Expected 20 fixes, got {len(fixes_a)}"
    assert len(dupes_f) == 0, f"Found duplicate fixes: {dupes_f}"
    assert len(missing_fields_f) == 0, f"Found missing fields in fixes: {missing_fields_f}"
    print("    [✓] PASS: 02b_FIXES has ZERO duplicates and ZERO missing fields.")

    # 3. TAB 02c_PAGES_CITATIONS
    ws_pc = wb["02c_PAGES_CITATIONS"]
    items_a = []
    missing_fields_pc = []
    pages_count = 0
    citations_count = 0
    for r in range(5, 55):
        item_id = ws_pc.cell(row=r, column=1).value
        item_type = ws_pc.cell(row=r, column=2).value
        if not item_id:
            continue
        items_a.append(item_id)
        if item_type == "Page":
            pages_count += 1
        elif item_type == "Citation target":
            citations_count += 1

        # Required: B(2), C(3), D(4), E(5), F(6), I(9)
        req_cols = [2, 3, 4, 5, 6, 9]
        empty_cols = [c for c in req_cols if not ws_pc.cell(row=r, column=c).value]
        if empty_cols:
            missing_fields_pc.append((item_id, empty_cols))

    dupes_pc = set([x for x in items_a if items_a.count(x) > 1])
    print(f"\n[*] 02c_PAGES_CITATIONS Total Populated: {len(items_a)} items ({pages_count} Pages, {citations_count} Citations)")
    print(f"    - Duplicates detected: {len(dupes_pc)}")
    print(f"    - Missing field rows: {len(missing_fields_pc)}")
    assert pages_count == 20, f"Expected 20 pages, got {pages_count}"
    assert citations_count == 30, f"Expected 30 citations, got {citations_count}"
    assert len(dupes_pc) == 0, f"Found duplicate items in 02c: {dupes_pc}"
    assert len(missing_fields_pc) == 0, f"Found missing fields in 02c: {missing_fields_pc}"
    print("    [✓] PASS: 02c_PAGES_CITATIONS has ZERO duplicates and ZERO missing fields.")

    # 4. TAB 04_SELF_CHECK
    ws4 = wb["04_SELF_CHECK"]
    print("\n[*] 04_SELF_CHECK Minimum Gates Verification:")
    gate_checks = [
        (6, "Real questions measured >= 100", ws4["C6"].value, lambda v: int(v) >= 100),
        (7, "AI assistants checked >= 4", ws4["C7"].value, lambda v: int(v) >= 4),
        (8, "Days measured >= 2", ws4["C8"].value, lambda v: int(v) >= 2),
        (9, "Validated technical fixes >= 20", ws4["C9"].value, lambda v: int(v) >= 20),
        (10, "Publish-ready pages >= 10", ws4["C10"].value, lambda v: int(v) >= 10),
        (11, "Citation targets >= 30", ws4["C11"].value, lambda v: int(v) >= 30),
        (12, "Tracker reruns from README = Yes", ws4["C12"].value, lambda v: str(v).lower() == "yes"),
    ]
    for row_idx, label, val, validator in gate_checks:
        is_met = validator(val)
        status = "MET" if is_met else "NOT MET"
        print(f"    - Row {row_idx}: {label:<35} Value: {val:<5} Status: {status}")
        assert is_met, f"Gate failed at row {row_idx}: {label} with value {val}"
    print("    [✓] PASS: All 7 minimum gates evaluate to 'MET'.")

    # 5. Exceptional Requirements (B17:B20)
    print("\n[*] 04_SELF_CHECK Exceptional Requirements (B17:B20):")
    for r in range(17, 21):
        achieved = ws4.cell(row=r, column=2).value
        val = ws4.cell(row=r, column=3).value
        evidence = ws4.cell(row=r, column=5).value
        print(f"    - Row {r}: Achieved: {achieved:<5} | Value: {str(val)[:40]}... | Evidence: {evidence}")
        assert achieved == "Yes", f"Row {r} achieved must be 'Yes'"
        assert val, f"Row {r} value must not be empty"
        assert evidence, f"Row {r} evidence must not be empty"
    print("    [✓] PASS: All 4 Exceptional Requirements are populated with evidence paths.")

    # 6. Green formulas check
    print("\n[*] Green Formulas Verification:")
    formulas_to_check = [
        ("02_QUESTIONS!U5", ws2["U5"].value),
        ("02_QUESTIONS!V5", ws2["V5"].value),
        ("02b_FIXES!K5", ws_fixes["K5"].value),
        ("02b_FIXES!L5", ws_fixes["L5"].value),
        ("02c_PAGES_CITATIONS!J5", ws_pc["J5"].value),
        ("02c_PAGES_CITATIONS!K5", ws_pc["K5"].value),
        ("00_START!B24", wb["00_START"]["B24"].value),
        ("00_START!B27", wb["00_START"]["B27"].value),
        ("04_SELF_CHECK!C29", ws4["C29"].value),
    ]
    for cell_ref, form in formulas_to_check:
        print(f"    - {cell_ref:<25}: {form}")
        assert str(form).startswith("="), f"Formula lost in {cell_ref}: {form}"
    print("    [✓] PASS: All calculation formulas are preserved untouched.")


def audit_repository_secrets():
    print("\n" + "=" * 70)
    print("  REPOSITORY SECRETS & LEAK AUDIT")
    print("=" * 70)

    # 1. Check git status and tracked files
    res = subprocess.run(["git", "ls-files"], capture_output=True, text=True)
    tracked_files = res.stdout.strip().splitlines()

    print(f"[*] Tracked files in git index: {len(tracked_files)}")
    assert ".env" not in tracked_files, "CRITICAL ERROR: .env file is tracked in git index!"

    # 2. Dynamically load tokens to test against from .env (without hardcoding them here)
    forbidden_tokens = []
    if os.path.exists(".env"):
        with open(".env", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    val = v.strip()
                    if len(val) > 12 and not val.lower() in ["false", "true", "sqlite", "utf-8"]:
                        forbidden_tokens.append(val)

    leaks = []
    this_script = os.path.abspath(__file__)
    for root, dirs, files in os.walk("."):
        if ".git" in root or ".pytest_cache" in root or "output" in root or "__pycache__" in root:
            continue
        for file in files:
            if file in [".env", ".env.example"]:
                continue # .env is local only and gitignored; .env.example has placeholders
            fpath = os.path.abspath(os.path.join(root, file))
            if fpath == this_script:
                continue
            try:
                with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    for token in forbidden_tokens:
                        if token in content:
                            leaks.append((os.path.relpath(fpath), token[:6] + "..."))
            except Exception:
                continue

    print(f"[*] Scanned source files: zero hardcoded secrets found.")
    assert len(leaks) == 0, f"Found hardcoded secrets in source files: {leaks}"
    print("    [✓] PASS: Zero API keys or secrets detected in repository code.")
    print("=" * 70)
    print("  ALL VERIFICATIONS PASSED SUCCESSFULLY")
    print("=" * 70)


if __name__ == "__main__":
    wb_file = "IncuBrix_2027_Growth_Engineer_Option_3_AEO_SEO_GEO_Submission_Workbook.xlsx"
    audit_workbook(wb_file)
    audit_repository_secrets()
