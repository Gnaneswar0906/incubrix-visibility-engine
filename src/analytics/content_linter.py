"""
src/analytics/content_linter.py
Automated quality linter for the 20 publish-ready content pages.
Enforces:
1. Word count >= 800 words
2. Answer-First rule: Direct answer in the first 2 sentences (20-60 words)
3. Zero unverified claims: Ensures roadmap features (e.g. digital avatars, voice cloning) are NOT claimed as live
4. Valid JSON-LD structured data (@context, @type, schema syntax)
5. Zero keyword stuffing: Primary keyword density < 4.0%
6. Presence of external authoritative source citations and internal IncuBrix links
Outputs:
- output/pages/content_linter_report.md
- output/pages/content_linter_summary.json
"""

import json
import os
import re
from typing import Any, Dict, List, Tuple


class ContentLinter:
    """
    Linter and quality auditor for publish-ready SEO/AEO/GEO content pages.
    """

    ROADMAP_TERMS_DISALLOWED_AS_LIVE = [
        "custom ai avatars are live",
        "voice cloning is live",
        "realtime voice cloning available now",
        "generate full video from text prompt without footage",
        "autonomous avatar generation live"
    ]

    def __init__(self, pages_dir: str = "output/pages", facts_path: str = "config/verified_product_facts.json"):
        # Resolve path
        cur = os.path.abspath(os.path.dirname(__file__))
        root = os.path.dirname(os.path.dirname(cur))
        self.base_dir = root if "incubrix-visibility-engine" in root else os.path.abspath(".")

        self.pages_dir = os.path.join(self.base_dir, pages_dir) if not os.path.isabs(pages_dir) else pages_dir
        self.facts_path = os.path.join(self.base_dir, facts_path) if not os.path.isabs(facts_path) else facts_path
        self.results: List[Dict[str, Any]] = []

    def lint_page(self, md_path: str, html_path: str) -> Dict[str, Any]:
        """Runs full quality audit on an individual page pair (MD + HTML)."""
        filename = os.path.basename(md_path)
        issues = []
        warnings = []

        with open(md_path, "r", encoding="utf-8") as f:
            md_text = f.read()

        html_text = ""
        if os.path.exists(html_path):
            with open(html_path, "r", encoding="utf-8") as f:
                html_text = f.read()

        # 1. Word Count Check (>= 800 words)
        words = md_text.split()
        word_count = len(words)
        if word_count < 800:
            issues.append(f"Word count below 800 threshold: {word_count} words")

        # 2. Answer-First Check (first 2 sentences)
        # Look for Quick Answer block
        qa_match = re.search(r'> \*\*Quick Answer:\*\*\s*(.*?)(?:\n\n|\n---)', md_text, re.DOTALL)
        if not qa_match:
            issues.append("Missing '> **Quick Answer:**' block at top of page")
            direct_answer_words = 0
        else:
            direct_ans = qa_match.group(1).strip()
            direct_answer_words = len(direct_ans.split())
            if direct_answer_words < 20:
                issues.append(f"Direct answer too brief ({direct_answer_words} words; minimum 20)")
            elif direct_answer_words > 75:
                warnings.append(f"Direct answer exceeds 75 words ({direct_answer_words} words)")

        # 3. Zero Unverified Claims
        lower_md = md_text.lower()
        for term in self.ROADMAP_TERMS_DISALLOWED_AS_LIVE:
            if term in lower_md:
                issues.append(f"Disallowed unverified claim found: '{term}'")

        # Check that pricing matches verified tiers
        if "$19" not in md_text and "Starter" in md_text:
            warnings.append("Starter plan mentioned without verified $19 price point")

        # 4. JSON-LD Structured Data Validation
        json_ld_valid = False
        json_ld_msg = "No HTML file found"
        if html_text:
            script_match = re.search(r'<script type="application/ld\+json">(.*?)</script>', html_text, re.DOTALL)
            if not script_match:
                issues.append("HTML missing <script type=\"application/ld+json\"> block")
                json_ld_msg = "Missing script block"
            else:
                raw_json = script_match.group(1).strip()
                try:
                    schema_data = json.loads(raw_json)
                    if "@context" not in schema_data:
                        issues.append("JSON-LD missing @context")
                        json_ld_msg = "Missing @context"
                    elif "@graph" not in schema_data and "@type" not in schema_data:
                        issues.append("JSON-LD missing @type or @graph")
                        json_ld_msg = "Missing @type/@graph"
                    else:
                        json_ld_valid = True
                        json_ld_msg = "Valid Schema.org syntax"
                except Exception as e:
                    issues.append(f"Invalid JSON-LD syntax: {str(e)}")
                    json_ld_msg = f"Syntax error: {str(e)}"

        # 5. Keyword Density & Stuffing Check
        # Extract title keyword candidate
        title_match = re.search(r'^#\s*(.*?)$', md_text, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else filename
        # Simple density calculation of 2-word combinations
        words_clean = [re.sub(r'[^\w\s]', '', w.lower()) for w in words]
        max_density = 0.0
        most_frequent_phrase = ""
        # Check title terms density
        title_terms = [t for t in title.lower().split() if len(t) > 3]
        for term in title_terms:
            cnt = words_clean.count(term)
            density = (cnt / len(words_clean)) * 100 if words_clean else 0
            if density > max_density:
                max_density = density
                most_frequent_phrase = term

        if max_density > 4.0:
            issues.append(f"High keyword density detected for '{most_frequent_phrase}': {max_density:.2f}% (max 4.0%)")

        # 6. Internal links and external citation checks
        has_internal_link = "incubrix.com" in md_text
        has_external_citation = ("http://" in md_text or "https://" in md_text) and ("hubspot" in md_text or "wistia" in md_text or "zapier" in md_text or "vidiq" in md_text or "searchengineland" in md_text or "sprout" in md_text)
        if not has_internal_link:
            issues.append("Page missing internal links to incubrix.com")
        if not has_external_citation:
            warnings.append("Page lacks standard external citations to authoritative benchmarks")

        passed = len(issues) == 0

        return {
            "file": filename,
            "title": title,
            "word_count": word_count,
            "direct_answer_words": direct_answer_words,
            "json_ld_valid": json_ld_valid,
            "json_ld_status": json_ld_msg,
            "max_keyword_density_pct": round(max_density, 2),
            "passed": passed,
            "issues": issues,
            "warnings": warnings
        }

    def lint_all_pages(self) -> List[Dict[str, Any]]:
        """Lints all P*.md pages in the output/pages directory."""
        if not os.path.exists(self.pages_dir):
            raise FileNotFoundError(f"Pages directory not found: {self.pages_dir}")

        md_files = sorted([f for f in os.listdir(self.pages_dir) if f.startswith("P") and f.endswith(".md")])
        results = []

        print("=" * 70)
        print("  CONTENT QUALITY LINTER & SCHEMA AUDIT")
        print(f"  Target: {self.pages_dir} ({len(md_files)} pages found)")
        print("=" * 70)

        for mf in md_files:
            md_path = os.path.join(self.pages_dir, mf)
            html_path = os.path.join(self.pages_dir, mf.replace(".md", ".html"))
            res = self.lint_page(md_path, html_path)
            results.append(res)
            status_symbol = "🟢 PASS" if res["passed"] else "🔴 FAIL"
            print(f"[{status_symbol}] {mf:<40} | Words: {res['word_count']:<4} | Direct Ans: {res['direct_answer_words']:<2}w | JSON-LD: {res['json_ld_status']}")

        self.results = results

        # Export JSON summary
        json_path = os.path.join(self.pages_dir, "content_linter_summary.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)

        # Export Markdown report
        report_path = os.path.join(self.pages_dir, "content_linter_report.md")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("# Content Quality & Schema Validation Report\n\n")
            f.write(f"**Total Pages Audited:** {len(results)}  \n")
            f.write(f"**Passed Pages:** {sum(1 for r in results if r['passed'])} / {len(results)}  \n\n")
            f.write("| Page ID | Title | Word Count | Direct Ans | JSON-LD | Status |\n")
            f.write("| :--- | :--- | :---: | :---: | :---: | :---: |\n")
            for r in results:
                st = "🟢 PASS" if r["passed"] else "🔴 FAIL"
                f.write(f"| `{r['file'][:3]}` | {r['title']} | {r['word_count']} words | {r['direct_answer_words']}w | {r['json_ld_status']} | {st} |\n")

        print("=" * 70)
        print(f"[✓] Linter complete. Reports saved to:\n    - {json_path}\n    - {report_path}")
        print("=" * 70)

        return results


def main():
    linter = ContentLinter()
    results = linter.lint_all_pages()
    assert all(r["passed"] for r in results), "Not all publish-ready pages passed quality linting!"


if __name__ == "__main__":
    main()
