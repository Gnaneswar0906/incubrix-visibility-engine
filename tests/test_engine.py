"""
tests/test_engine.py
Comprehensive test suite for the IncuBrix Visibility Engine.
Tests:
1. Schema validation & dropdown enum enforcement (rejects 'UK', invalid enums)
2. Exact duplicate rejection & deduplication state
3. Refresh idempotency & Day 1 -> Day 2 diffing
4. API failure recovery & exponential backoff
5. Programmatic generation & JSON-LD validation
6. Workbook formula preservation & cell safety
"""

import os
import shutil
import tempfile
import pytest
import openpyxl

from src.collectors.llm_collector import LLMCollector
from src.collectors.serp_collector import SerpCollector
from src.exporters.workbook_sync import WorkbookSync
from src.models import (
    AnswerBoxEnum,
    ChangedDay2Enum,
    IntentEnum,
    MarketEnum,
    PriorityEnum,
    QuestionRecord,
    VisibilityStatusEnum,
)
from src.programmatic.generator import ProgrammaticGenerator
from src.storage.db import Database


# -----------------------------------------------------------------------------
# Fixtures
# -----------------------------------------------------------------------------
@pytest.fixture
def temp_db():
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test_visibility.db")
    db = Database(db_path=db_path)
    yield db
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def sample_question():
    return QuestionRecord(
        question_id="Q001",
        question="how to turn a 1-hour podcast into viral shorts automatically",
        intent=IntentEnum.INFORMATIONAL,
        source_type="Reddit r/NewTubers",
        source_url="https://reddit.com/r/NewTubers",
        market=MarketEnum.US,
        google_position=2,
        answer_box_or_ai_overview=AnswerBoxEnum.BOTH,
        quoted_source_url="https://incubrix.com/blog/repurpose-guide",
        chatgpt=VisibilityStatusEnum.CITED,
        gemini=VisibilityStatusEnum.MENTIONED,
        perplexity=VisibilityStatusEnum.CITED,
        claude_or_copilot=VisibilityStatusEnum.MENTIONED,
        competitors_named="CapCut, Opus Clip",
        check_date_day1="2026-11-20",
        check_date_day2="2026-11-21",
        changed_on_day2=ChangedDay2Enum.NO,
        raw_answers_url="output/raw_evidence/serp/serp_q001_us.json",
        priority=PriorityEnum.HIGH,
        notes="Strategic high-intent query"
    )


# -----------------------------------------------------------------------------
# Test 1: Schema Validation & Enum Enforcement
# -----------------------------------------------------------------------------
def test_schema_valid_record(sample_question):
    """Verifies that a compliant record produces exact 20-column dictionary and Excel row."""
    d = sample_question.to_dict_20_columns()
    assert len(d) == 20
    assert d["market"] == "US"
    assert d["intent"] == "Informational"

    row = sample_question.to_excel_row()
    assert len(row) == 20
    assert row[0] == "Q001"
    assert row[1] == "how to turn a 1-hour podcast into viral shorts automatically"


def test_schema_rejects_uk_market():
    """Rule: NEVER use 'UK', always 'GB'. Rejection must be enforced."""
    with pytest.raises(ValueError, match="Invalid market 'UK'"):
        QuestionRecord(
            question_id="Q999",
            question="test query for uk market",
            intent=IntentEnum.INFORMATIONAL,
            source_type="Google",
            source_url="https://google.com",
            market="UK",  # Should trigger validator
            google_position=1,
            answer_box_or_ai_overview=AnswerBoxEnum.NONE,
            quoted_source_url="",
            chatgpt=VisibilityStatusEnum.NOT_MENTIONED,
            gemini=VisibilityStatusEnum.NOT_MENTIONED,
            perplexity=VisibilityStatusEnum.NOT_MENTIONED,
            claude_or_copilot=VisibilityStatusEnum.NOT_MENTIONED,
            competitors_named="",
            check_date_day1="2026-11-20",
            check_date_day2="2026-11-21",
            changed_on_day2=ChangedDay2Enum.NO,
            raw_answers_url="",
            priority=PriorityEnum.MEDIUM,
            notes=""
        )


def test_schema_rejects_blank_question():
    """Question cannot be blank."""
    with pytest.raises(ValueError, match="cannot be blank"):
        QuestionRecord(
            question_id="Q998",
            question="   ",
            intent=IntentEnum.INFORMATIONAL,
            source_type="Google",
            source_url="https://google.com",
            market=MarketEnum.GB,
            google_position=1,
            answer_box_or_ai_overview=AnswerBoxEnum.NONE,
            quoted_source_url="",
            chatgpt=VisibilityStatusEnum.NOT_MENTIONED,
            gemini=VisibilityStatusEnum.NOT_MENTIONED,
            perplexity=VisibilityStatusEnum.NOT_MENTIONED,
            claude_or_copilot=VisibilityStatusEnum.NOT_MENTIONED,
            competitors_named="",
            check_date_day1="2026-11-20",
            check_date_day2="2026-11-21",
            changed_on_day2=ChangedDay2Enum.NO,
            raw_answers_url="",
            priority=PriorityEnum.MEDIUM,
            notes=""
        )


# -----------------------------------------------------------------------------
# Test 2: Deduplication State
# -----------------------------------------------------------------------------
def test_sqlite_deduplication(temp_db, sample_question):
    """Verifies that inserting the exact same question updates rather than duplicates."""
    ins1, upd1 = temp_db.upsert_question(sample_question, day=1)
    assert ins1 is True
    assert upd1 is False
    assert temp_db.get_question_count() == 1

    # Attempt second insertion of same question with different ID
    dup_record = sample_question.model_copy(update={"question_id": "Q002"})
    ins2, upd2 = temp_db.upsert_question(dup_record, day=1)
    assert ins2 is False
    assert upd2 is True
    assert temp_db.get_question_count() == 1


# -----------------------------------------------------------------------------
# Test 3: Refresh Idempotency & Day 1 -> Day 2 Diffing
# -----------------------------------------------------------------------------
def test_refresh_idempotency_and_diff(temp_db, sample_question):
    """Verifies that Day 2 refresh computes metric diff and sets changed_on_day2='Yes'."""
    temp_db.upsert_question(sample_question, day=1)
    assert temp_db.get_question_count() == 1

    # Update on Day 2 with changed position
    d2_record = sample_question.model_copy(update={
        "google_position": 8,
        "chatgpt": VisibilityStatusEnum.MENTIONED
    })
    ins, upd = temp_db.upsert_question(d2_record, day=2)
    assert ins is False
    assert upd is True
    assert temp_db.get_question_count() == 1

    all_q = temp_db.get_all_questions()
    assert len(all_q) == 1
    assert all_q[0].changed_on_day2 == ChangedDay2Enum.YES

    diffs = temp_db.get_diff_summary()
    assert diffs["changed_question_count"] == 1
    assert diffs["total_diff_events"] >= 1


# -----------------------------------------------------------------------------
# Test 4: API Failure Recovery & Exponential Backoff
# -----------------------------------------------------------------------------
def test_serp_failure_recovery():
    """Verifies SERP collector handles simulated network drop with retry backoff."""
    collector = SerpCollector(offline_mode=True, simulate_failure=True)
    res = collector.collect("how to repurpose video for TikTok", MarketEnum.US, retries=2, backoff_sec=0.05)
    assert res is not None
    assert "google_position" in res
    assert "answer_box_or_ai_overview" in res


def test_llm_failure_recovery():
    """Verifies LLM collector handles simulated rate limit with retry backoff."""
    collector = LLMCollector(runs_per_question=2, offline_mode=True, simulate_failure=True)
    res = collector.collect_assistant_visibility("chatgpt", "best ai video clipping tool", MarketEnum.US, retries=2, backoff_sec=0.05)
    assert res is not None
    assert "final_status" in res
    assert res["final_status"] in ["Cited", "Mentioned", "Not mentioned"]
    assert len(res["runs"]) == 2


# -----------------------------------------------------------------------------
# Test 5: Programmatic Page Generation & JSON-LD Validation
# -----------------------------------------------------------------------------
def test_programmatic_generation():
    """Verifies that programmatic pages render valid HTML with parseable JSON-LD."""
    temp_dir = tempfile.mkdtemp()
    try:
        gen = ProgrammaticGenerator(
            matrix_path="data/programmatic_matrix.csv",
            output_dir=temp_dir
        )
        res = gen.generate_all_pages()
        assert res["successfully_generated"] >= 100
        assert res["quality_failures_count"] == 0

        # Check rendered HTML
        files = os.listdir(temp_dir)
        html_files = [f for f in files if f.endswith(".html")]
        assert len(html_files) >= 100

        with open(os.path.join(temp_dir, html_files[0]), "r", encoding="utf-8") as f:
            content = f.read()
            assert '<script type="application/ld+json">' in content
            assert '"@context": "https://schema.org"' in content
            assert 'Direct Answer:' in content
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


# -----------------------------------------------------------------------------
# Test 6: Workbook Integrity & Formula Preservation
# -----------------------------------------------------------------------------
def test_workbook_sync_preserves_formulas():
    """Verifies openpyxl sync writes only yellow cells and preserves green formulas."""
    temp_dir = tempfile.mkdtemp()
    try:
        template_src = "IncuBrix_2027_Growth_Engineer_Option_3_AEO_SEO_GEO_Submission_Workbook.xlsx"
        if not os.path.exists(template_src):
            template_src = os.path.join("..", template_src)

        test_wb_copy = os.path.join(temp_dir, "test_workbook.xlsx")
        shutil.copy2(template_src, test_wb_copy)

        # Sync with sample records
        sample_records = [
            QuestionRecord(
                question_id=f"Q{i:03d}",
                question=f"Unique creator query text number {i} for video repurposing",
                intent=IntentEnum.INFORMATIONAL,
                source_type="Google Suggest",
                source_url="https://google.com",
                market=MarketEnum.US,
                google_position=1,
                answer_box_or_ai_overview=AnswerBoxEnum.AI_OVERVIEW,
                quoted_source_url="https://incubrix.com",
                chatgpt=VisibilityStatusEnum.CITED,
                gemini=VisibilityStatusEnum.MENTIONED,
                perplexity=VisibilityStatusEnum.CITED,
                claude_or_copilot=VisibilityStatusEnum.MENTIONED,
                competitors_named="CapCut",
                check_date_day1="2026-11-20",
                check_date_day2="2026-11-21",
                changed_on_day2=ChangedDay2Enum.NO,
                raw_answers_url="output/raw_evidence/serp/test.json",
                priority=PriorityEnum.HIGH,
                notes="Verified test item"
            )
            for i in range(1, 105)
        ]

        sync = WorkbookSync(
            template_path=test_wb_copy,
            output_csv_path=os.path.join(temp_dir, "test_vis.csv"),
            output_xlsx_path=test_wb_copy
        )
        sync.sync_workbook(sample_records)

        # Inspect modified workbook
        wb = openpyxl.load_workbook(test_wb_copy, data_only=False)

        # Check Tab 02_QUESTIONS formulas
        ws02 = wb["02_QUESTIONS"]
        assert ws02["U5"].value == '=IF(A5="","",IF(COUNTIF($B$5:$B$304,B5)>1,"DUPLICATE","UNIQUE"))'
        assert ws02["V5"].value == '=IF(A5="","",IF(AND(B5<>"",C5<>"",D5<>"",E5<>"",F5<>"",G5<>"",H5<>"",J5<>"",K5<>"",L5<>"",M5<>"",O5<>"",P5<>"",R5<>""),"COMPLETE","MISSING FIELDS"))'

        # Check Tab 04_SELF_CHECK formulas
        ws04 = wb["04_SELF_CHECK"]
        assert ws04["D6"].value == '=COUNTA(02_QUESTIONS!B5:B304)'
        assert ws04["F6"].value == '=IF(C6="","",IF(C6>=100,"MET","NOT MET"))'
        assert ws04["C29"].value == '=SUM(C24:C28)'

        # Check Tab 00_START formulas
        ws00 = wb["00_START"]
        assert ws00["B24"].value == '=COUNTIF(04_SELF_CHECK!F6:F12,"MET")&" of 7"'
        assert ws00["B26"].value == '=IF(B21="Yes","Yes","NOT YET")'
        assert ws00["B27"].value == '=IF(AND(COUNTIF(04_SELF_CHECK!F6:F12,"MET")=7,B21="Yes",COUNTIF(F5:F10,"Yes")=6),"YES","NOT YET - check tabs 00 and 04")'

        # Check Tab 02b_FIXES formulas
        ws02b = wb["02b_FIXES"]
        assert ws02b["K5"].value == '=IF(A5="","",IF(COUNTIF($A$5:$A$54,A5)>1,"DUPLICATE","UNIQUE"))'
        assert ws02b["L5"].value == '=IF(A5="","",IF(AND(B5<>"",C5<>"",D5<>"",E5<>"",F5<>"",G5<>"",H5<>"",I5<>""),"COMPLETE","MISSING FIELDS"))'

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


# -----------------------------------------------------------------------------
# Test 7: Technical Fixes and Validation
# -----------------------------------------------------------------------------
def test_technical_fixes_and_validation():
    """Verifies that 20 technical fixes exist, adhere to schema, and pass validation."""
    fixes_csv = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output", "fixes", "fixes_table.csv")
    if not os.path.exists(fixes_csv):
        pytest.skip("fixes_table.csv not generated yet")

    import csv
    with open(fixes_csv, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    assert len(rows) == 20, f"Expected 20 fixes, got {len(rows)}"

    expected_cols = {
        "fix_id", "page_url", "problem", "evidence_url", "fix_summary",
        "code_or_text_url", "validator_used", "validated", "impact", "effort"
    }
    assert set(rows[0].keys()) == expected_cols

    for row in rows:
        assert row["fix_id"].startswith("FIX")
        assert row["validated"] == "Yes"
        assert row["impact"] in {"High", "Medium", "Low"}
        assert row["effort"] in {"High", "Medium", "Low"}


# -----------------------------------------------------------------------------
# Test 8: 20 Publish-Ready Pages & Content Linter
# -----------------------------------------------------------------------------
def test_publish_pages_and_content_linter():
    """Verifies that 20 publish-ready pages exist, exceed 800 words, and pass linting."""
    from src.analytics.content_linter import ContentLinter
    pages_csv = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output", "pages", "pages_table.csv")
    if not os.path.exists(pages_csv):
        pytest.skip("pages_table.csv not generated yet")

    import csv
    with open(pages_csv, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    assert len(rows) == 20, f"Expected 20 publish pages, got {len(rows)}"

    linter = ContentLinter()
    lint_results = linter.lint_all_pages()
    assert len(lint_results) == 20
    for res in lint_results:
        assert res["word_count"] >= 800, f"Page {res['file']} has {res['word_count']} words (<800)"
        assert res["direct_answer_words"] >= 20, f"Page {res['file']} direct answer too brief"
        assert res["json_ld_valid"] is True, f"Page {res['file']} invalid JSON-LD"
        assert res["passed"] is True, f"Page {res['file']} failed linting: {res['issues']}"


# -----------------------------------------------------------------------------
# Test 9: 120 Programmatic Pages & Audit Summary
# -----------------------------------------------------------------------------
def test_programmatic_audit_summary():
    """Verifies 120 programmatic pages generated and audit summary is valid."""
    summary_csv = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output", "programmatic_pages", "programmatic_audit_summary.csv")
    if not os.path.exists(summary_csv):
        pytest.skip("programmatic_audit_summary.csv not generated yet")

    import csv
    with open(summary_csv, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    assert len(rows) == 120, f"Expected 120 programmatic audit rows, got {len(rows)}"
    slugs = set()
    for row in rows:
        assert row["slug"] not in slugs, f"Duplicate slug detected: {row['slug']}"
        slugs.add(row["slug"])
        assert int(row["word_count"]) >= 400
        assert row["json_ld_valid"] == "PASS"
        assert row["thin_content_check"] == "PASS"
        assert row["status"] == "PASS"


