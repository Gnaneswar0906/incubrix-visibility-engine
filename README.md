# IncuBrix AEO, SEO & GEO Visibility Engine

> **Production-grade Search, Answer Engine (AEO), and Generative Engine Optimization (GEO) tracker for IncuBrix ([incubrix.com](https://incubrix.com)).**  
> Tracks Google search rankings, Answer Boxes (featured snippets), Google AI Overviews, and 4 major AI assistants (**ChatGPT, Gemini, Perplexity, Claude/Copilot**), with SQLite deduplication state, multi-region markets, Day 1 vs Day 2 diffing, 105 programmatic landing pages, and automated Excel submission workbook population.

---

## 🚀 One-Command Quickstart

To run the entire end-to-end engine (ingestion, deduplication, visibility measurement, report generation, and Excel workbook synchronization):

```bash
python -m src.cli run --input data/questions_seed.csv
```

---

## 📋 Core CLI Commands

The engine provides a single unified entry point `src/cli.py` supporting all key operations:

### 1. Normal Execution Run (Day 1 Baseline)
Ingests seed queries, runs multi-assistant and SERP collection, persists to SQLite, exports `output/visibility.csv`, and syncs `IncuBrix_2027_Growth_Engineer_Option_3_AEO_SEO_GEO_Submission_Workbook.xlsx`:
```bash
python -m src.cli run --input data/questions_seed.csv
```

### 2. Day 2 Refresh & Diffing
Reruns queries on Day 2, detects non-deterministic variance and metric changes, updates `changed_on_day2`, and updates the workbook:
```bash
python -m src.cli refresh --input data/questions_seed.csv
```

### 3. Generate 120 Programmatic SEO/AEO Pages
Generates 120 quality-checked HTML & companion Markdown pages across two scalable templates (60 workflow pages + 60 persona pages) with JSON-LD schema (`HowTo` and `FAQPage`) and audit summary:
```bash
python -m src.cli programmatic --matrix data/programmatic_matrix.csv
```

### 4. Generate 20 Publish-Ready Answer-First Pages
Renders 20 in-depth (>1,200 words) authoritative pages with answer-first summaries, verified product claims, external citations, and embedded Schema.org JSON-LD, then runs the quality linter:
```bash
python -m src.cli pages
```

### 5. Generate Content Briefs for High-Priority Query Gaps
Identifies high-priority queries where IncuBrix is currently not mentioned and outputs structured content briefs with direct answer boxes:
```bash
python -m src.cli brief --limit 15
```

### 6. Automated Self-Audit Verification
Validates the entire submission against every workbook constraint (checks uniqueness of questions, presence of 4 AI assistants, 2 measurement days, 20 technical fixes, 20 publish pages, 30 citation targets, and green formulas):
```bash
python -m src.cli self-audit
```

### 7. Live Technical SEO, AEO & GEO Site Audit
Crawls `https://incubrix.com`, inspects `/robots.txt`, `/sitemap.xml`, `/llms.txt`, heading hierarchy, mixed HTTP links, and structured data, producing 20 ready-to-paste fixes:
```bash
python src/analytics/site_auditor.py
```

### 8. Standalone Technical Fixes Validator
Validates Schema.org JSON-LD, robots.txt directives, llmstxt.org specs, and HTML syntax for all 20 fixes, generating proof logs in `output/fixes/validation_results/`:
```bash
python src/analytics/validate_fixes.py
```

### 9. Real Third-Party Citation Extraction
Parses live SERP answer boxes, AI Overviews, and AI assistant responses across all 300 queries, ranking the top 30 third-party domains and exporting `output/pages/citations_table.csv` (rows `C01`–`C30` in Tab `02c_PAGES_CITATIONS`):
```bash
python -m src.analytics.citation_extractor
```

### 10. Owned-Site Before-and-After AEO/GEO Verification Site (`owned_site_demo/`)
A complete, deployment-ready static website configured for Vercel or GitHub Pages to verify before-and-after indexing impact:
- `index.html`: Responsive homepage with embedded `SoftwareApplication` + `Organization` + `FAQPage` JSON-LD
- `guides/`: 5 publish-ready creator workflow guides with `HowTo` and `Article` Schema.org markup
- `llms.txt`: Standardized AI specification per https://llmstxt.org
- `robots.txt`: Permissive directives allowing GPTBot, ClaudeBot, PerplexityBot, and Google-Extended
- `sitemap.xml`: Complete XML sitemap
- `vercel.json`: Production deployment configuration with caching and CORS headers

```bash
cd owned_site_demo
npx vercel --prod
```

### 11. Simulated API Failure & Exponential Backoff Recovery
Tests resilience by simulating network drops and rate limits, proving graceful recovery:
```bash
python -m src.cli run --input data/questions_seed.csv --simulate-failure
```

### 12. 45-Minute Live Review & Technical Demo Video (`data/live_review_sample.csv`)
For instant live demonstration during technical interviews, run this lightweight 5-question test harness that executes end-to-end collection, SQLite diffing, and export in ~5 seconds:
```bash
python -m src.cli run --input data/live_review_sample.csv
```

---

## 🧪 Unit & Integration Tests

Run the complete test suite with `pytest`:

```bash
pytest tests/ -v
```

The test suite covers:
- **`test_schema_validation`**: Validates strict enums, rejects invalid inputs (e.g. raises error on `UK`, enforcing `GB`).
- **`test_duplicate_rejection`**: Tests SQLite unique constraint on question text and duplicate deduplication.
- **`test_refresh_idempotency`**: Tests that re-running existing queries updates metrics and diffs without creating duplicate rows.
- **`test_api_failure_recovery`**: Tests exponential backoff retries on SERP and LLM collector failures.
- **`test_programmatic_generation`**: Validates 100+ generated pages and verifies valid syntax for JSON-LD structured data.
- **`test_workbook_sync_preserves_formulas`**: Verifies that openpyxl writes strictly to yellow cells and preserves green formulas.

---

## 📊 Exact Workbook & Schema Rules Compliance

| Requirement | Implementation & Safety Mechanism |
| :--- | :--- |
| **Exact 20 Input Columns** | `visibility.csv` and `02_QUESTIONS` strictly enforce: `question_id, question, intent, source_type, source_url, market, google_position, answer_box_or_ai_overview, quoted_source_url, chatgpt, gemini, perplexity, claude_or_copilot, competitors_named, check_date_day1, check_date_day2, changed_on_day2, raw_answers_url, priority, notes` |
| **Strict Dropdown Enums** | Enforced in `src/models.py`: `intent` (Informational, Comparison, Transactional, Navigational), `market` (US, GB, CA, AU, IN, SG, Other - NEVER UK), `answer_box_or_ai_overview` (Answer box, AI Overview, Both, None), assistants (Cited, Mentioned, Not mentioned), `changed_on_day2` (Yes, No), `priority` (High, Medium, Low). |
| **Question Uniqueness** | Excel formula `=IF(COUNTIF($B$5:$B$304,B5)>1,"DUPLICATE","UNIQUE")` checks uniqueness on `question` (Col B). SQLite database enforces `UNIQUE(question)` and memory deduplication removes any colliding queries. |
| **Preserving Green Cells** | `WorkbookSync` writes **only** to yellow input cells (Cols A to T in `02_QUESTIONS`, A to J in `02b_FIXES`, A to I in `02c_PAGES_CITATIONS`, etc.). Green calculation formulas in `00_START`, `02_QUESTIONS`, `02b_FIXES`, `02c_PAGES_CITATIONS`, and `04_SELF_CHECK` remain untouched and evaluate to **MET** and **100/100**. |
| **Zero Hardcoded Secrets** | API keys load from `.env` or environment variables; offline deterministic mock fallback ensures zero-cost reproduction for reviewers. |

---

## 📁 Repository Structure

```
incubrix-visibility-engine/
├── README.md                                          # Complete instructions and single run command
├── requirements.txt                                   # Production dependencies
├── .env.example                                       # API configuration template
├── .gitignore                                         # Git ignore rules
├── config/
│   ├── settings.yaml                                  # Engine parameters & brand configuration
│   └── verified_product_facts.json                    # Single source of truth for pricing, features & roadmap flags
├── src/
│   ├── __init__.py
│   ├── cli.py                                         # Single entry point supporting all subcommands
│   ├── models.py                                      # Pydantic schemas enforcing exact workbook dropdowns
│   ├── collectors/
│   │   ├── question_harvester.py                      # Multi-market Google/YouTube/Forum autocomplete harvester (300 queries)
│   │   ├── serp_collector.py                          # Multi-region Google SERP & Answer Box collector
│   │   └── llm_collector.py                           # 4 AI assistants (chatgpt, gemini, perplexity, claude)
│   ├── storage/
│   │   └── db.py                                      # SQLite persistence, deduplication & Day 1/2 diffing
│   ├── analytics/
│   │   ├── site_auditor.py                            # Live technical SEO/AEO/GEO audit crawler & fix generator
│   │   ├── validate_fixes.py                          # Schema.org JSON-LD, robots, llms, HTML validator
│   │   ├── content_linter.py                          # Quality & schema linter for 20 publish-ready pages
│   │   ├── citation_extractor.py                      # Extracts top 30 third-party citation targets from live runs
│   │   ├── reporter.py                                # Generates weekly_visibility_report.md
│   │   └── brief_generator.py                         # Generates structured content briefs for gaps
│   ├── programmatic/
│   │   ├── matrix_builder.py                          # Generates 120 workflow & persona combinations
│   │   ├── publish_pages_generator.py                 # Generates 20 publish-ready answer-first pages
│   │   └── generator.py                               # 120 programmatic pages with JSON-LD validation
│   └── exporters/
│       └── workbook_sync.py                           # Openpyxl workbook auto-populator
├── templates/
│   └── programmatic_page.html.j2                      # Jinja2 template with Answer Box & Schema.org markup
├── data/
│   ├── questions_seed.csv                             # 300 unique real creator queries across 3 markets
│   └── programmatic_matrix.csv                        # 120 programmatic matrix combinations (60 workflow + 60 persona)
├── output/
│   ├── visibility.csv                                 # Official 20-column visibility export
│   ├── raw_evidence/                                  # SERP, assistant, and live site audit raw snapshots
│   ├── fixes/                                         # 20 technical fixes with code and validator evidence
│   ├── pages/                                         # 20 publish-ready pages (MD & HTML) + pages_table.csv
│   ├── programmatic_pages/                            # 120 HTML & MD programmatic pages + audit summary
│   └── reports/                                       # weekly_visibility_report.md
├── owned_site_demo/                                   # Complete deployable static site (Vercel / GitHub Pages)
│   ├── index.html                                     # Homepage with SoftwareApplication & FAQPage JSON-LD
│   ├── llms.txt                                       # Standardized machine-readable AI documentation
│   ├── robots.txt                                     # AI-friendly bot directives allowing GPTBot, ClaudeBot, etc.
│   ├── sitemap.xml                                    # Complete XML sitemap
│   ├── vercel.json                                    # Vercel deployment headers and clean URL routing
│   ├── README.md                                      # Before-and-after testing instructions
│   └── guides/                                        # 5 publish-ready creator workflow guides (HowTo / Article Schema)
├── tests/
│   └── test_engine.py                                 # Pytest suite
└── .github/
    └── workflows/
        └── weekly_tracker.yml                         # Weekly automated cron workflow & webhook alerting
```

---

## 🔄 Scheduled Weekly Tracking (CI/CD)

The repository includes `.github/workflows/weekly_tracker.yml` which:
1. Triggers every Monday at 06:00 UTC via GitHub Actions cron.
2. Ingests questions, runs Day 2 refresh, and diffs visibility changes.
3. Renders programmatic landing pages and gap briefs.
4. Generates `output/reports/weekly_visibility_report.md`.
5. Verifies self-audit and runs the `pytest` test suite.
6. Posts alert summaries via webhook if visibility drops below target thresholds.
7. Archives all reports, CSVs, and the updated Excel workbook as workflow artifacts.
