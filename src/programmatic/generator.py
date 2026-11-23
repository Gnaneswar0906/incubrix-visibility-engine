"""
src/programmatic/generator.py
Jinja2 programmatic engine producing 100+ quality-checked HTML and Markdown pages
with JSON-LD schema validation, answer-first copywriting, and meta-tag optimization.
"""

import csv
import json
import os
import re
from typing import Any, Dict, List, Tuple
from jinja2 import Environment, FileSystemLoader
from src.models import MarketEnum, ProgrammaticRow


class ProgrammaticGenerator:
    """
    Renders 100+ SEO/AEO/GEO programmatic landing pages from matrix data.
    Validates JSON-LD schema structure and answer-first quality rules.
    """

    def __init__(
        self,
        matrix_path: str = "data/programmatic_matrix.csv",
        template_dir: str = "templates",
        template_name: str = "programmatic_page.html.j2",
        output_dir: str = "output/programmatic_pages"
    ):
        self.matrix_path = matrix_path
        self.output_dir = output_dir
        self.template_dir = template_dir
        self.template_name = template_name
        os.makedirs(self.output_dir, exist_ok=True)

        self.env = Environment(
            loader=FileSystemLoader(self.template_dir),
            autoescape=True
        )

    def load_matrix(self) -> List[ProgrammaticRow]:
        """Loads and parses the programmatic matrix rows."""
        rows = []
        if not os.path.exists(self.matrix_path):
            raise FileNotFoundError(f"Matrix CSV not found at: {self.matrix_path}")

        with open(self.matrix_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for r in reader:
                market_val = r.get("market", "US").strip()
                if market_val.upper() == "UK":
                    market_val = "GB"
                elif market_val.upper() == "OTHER":
                    market_val = "Other"
                else:
                    market_val = market_val.upper()

                rows.append(ProgrammaticRow(
                    topic=r["topic"].strip(),
                    target_platform=r["target_platform"].strip(),
                    persona=r["persona"].strip(),
                    market=MarketEnum(market_val),
                    title=r["title"].strip(),
                    slug=r["slug"].strip(),
                    primary_kw=r["primary_kw"].strip(),
                    direct_answer=r["direct_answer"].strip(),
                    json_ld_type=r.get("json_ld_type", "FAQPage").strip()
                ))
        return rows

    def _validate_json_ld(self, html_content: str) -> Tuple[bool, str]:
        """Extracts and verifies JSON-LD structured data syntax."""
        pattern = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.DOTALL)
        match = pattern.search(html_content)
        if not match:
            return False, "Missing JSON-LD script block"

        raw_json = match.group(1).strip()
        try:
            data = json.loads(raw_json)
            if "@context" not in data or "@type" not in data:
                return False, "JSON-LD missing @context or @type"
            return True, "Valid JSON-LD"
        except Exception as e:
            return False, f"Invalid JSON syntax: {str(e)}"

    def _validate_quality(self, row: ProgrammaticRow, html_content: str) -> List[str]:
        """Performs programmatic SEO quality checks."""
        issues = []
        # Check Answer-First rule (direct answer must be present and >= 20 words)
        words = row.direct_answer.split()
        if len(words) < 20:
            issues.append(f"Direct answer too brief ({len(words)} words; minimum 20)")

        # Title length check
        if len(row.title) < 20 or len(row.title) > 100:
            issues.append(f"Title length out of bounds ({len(row.title)} chars)")

        # Validate JSON-LD
        valid_json, msg = self._validate_json_ld(html_content)
        if not valid_json:
            issues.append(f"Structured data error: {msg}")

        # Check thin content (> 400 words in HTML body)
        text_only = re.sub(r'<[^>]+>', ' ', html_content)
        total_words = len(text_only.split())
        if total_words < 400:
            issues.append(f"Thin content warning: {total_words} words (minimum 400)")

        return issues

    def generate_all_pages(self) -> Dict[str, Any]:
        """
        Renders all programmatic pages, validates them, and persists HTML & Markdown files.
        Generates output/programmatic_pages/programmatic_audit_summary.csv.
        """
        matrix_rows = self.load_matrix()
        template = self.env.get_template(self.template_name)

        success_count = 0
        quality_failures = []
        generated_slugs = set()
        audit_rows = []

        for row in matrix_rows:
            # Enforce unique slugs
            slug = row.slug
            if slug in generated_slugs:
                slug = f"{slug}-{row.market.value.lower()}"
            generated_slugs.add(slug)

            rendered_html = template.render(
                topic=row.topic,
                target_platform=row.target_platform,
                persona=row.persona,
                market=row.market.value,
                title=row.title,
                slug=slug,
                primary_kw=row.primary_kw,
                direct_answer=row.direct_answer,
                json_ld_type=row.json_ld_type
            )

            # Quality validation
            issues = self._validate_quality(row, rendered_html)
            if issues:
                quality_failures.append({"slug": slug, "issues": issues})

            # Calculate metrics for audit summary
            text_only = re.sub(r'<[^>]+>', ' ', rendered_html)
            word_count = len(text_only.split())
            valid_json, _ = self._validate_json_ld(rendered_html)
            thin_content_pass = word_count >= 400

            audit_rows.append({
                "slug": slug,
                "title": row.title,
                "market": row.market.value,
                "target_platform": row.target_platform,
                "persona": row.persona,
                "word_count": word_count,
                "json_ld_type": row.json_ld_type,
                "json_ld_valid": "PASS" if valid_json else "FAIL",
                "thin_content_check": "PASS" if thin_content_pass else "FAIL",
                "status": "PASS" if not issues else "FAIL"
            })

            # Save HTML
            html_path = os.path.join(self.output_dir, f"{slug}.html")
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(rendered_html)

            # Save Markdown companion
            md_path = os.path.join(self.output_dir, f"{slug}.md")
            md_content = f"""# {row.title}
**Market:** {row.market.value} | **Platform:** {row.target_platform} | **Persona:** {row.persona}  
**URL:** https://incubrix.com/solutions/{slug}  

## Direct Answer
{row.direct_answer}

## Workflow & Features
- Automated highlights and transcriptions (99.2% accuracy)
- AI kinetic captioning in 40+ languages
- Fast 9:16 vertical video active speaker reformatting
- Cloud-accelerated rendering in under 90 seconds
- 1-click batch publishing to {row.target_platform}
"""
            with open(md_path, "w", encoding="utf-8") as f:
                f.write(md_content)

            success_count += 1

        # Export programmatic_audit_summary.csv
        summary_csv_path = os.path.join(self.output_dir, "programmatic_audit_summary.csv")
        fieldnames = [
            "slug", "title", "market", "target_platform", "persona",
            "word_count", "json_ld_type", "json_ld_valid", "thin_content_check", "status"
        ]
        with open(summary_csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(audit_rows)

        print(f"[✓] Saved programmatic audit summary to: {summary_csv_path}")

        return {
            "total_processed": len(matrix_rows),
            "successfully_generated": success_count,
            "quality_failures_count": len(quality_failures),
            "quality_failures": quality_failures,
            "output_directory": self.output_dir,
            "summary_csv": summary_csv_path
        }
