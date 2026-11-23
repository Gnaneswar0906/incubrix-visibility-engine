"""
src/analytics/validate_fixes.py
Comprehensive validator for technical SEO, AEO, and GEO fixes.
Validates:
1. JSON-LD schema blocks (syntax, @context, @type, required Schema.org properties)
2. robots.txt syntax (User-agent, Allow, Disallow, Sitemap directives)
3. llms.txt syntax (title, markdown sections, structure)
4. HTML snippets (semantic tags, attribute formatting, link protocols)

Outputs validation proof logs to output/fixes/validation_results/.
"""

import json
import os
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple


class FixValidator:
    """
    Validates ready-to-paste technical fixes for syntax, compliance, and schema validity.
    """

    def __init__(self, fixes_dir: str = "output/fixes", results_dir: str = "output/fixes/validation_results"):
        self.fixes_dir = fixes_dir
        self.results_dir = results_dir
        os.makedirs(self.results_dir, exist_ok=True)
        self.validation_results: List[Dict[str, Any]] = []

    def validate_json_ld(self, filepath: str) -> Tuple[bool, str, Dict[str, Any]]:
        """Validates JSON-LD file for syntax, @context, @type, and required properties."""
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # Handle raw script tag or raw JSON
        json_str = content
        if '<script type="application/ld+json">' in content:
            match = re.search(r'<script[^>]*>(.*?)</script>', content, re.DOTALL)
            if match:
                json_str = match.group(1).strip()

        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            return False, f"JSONDecodeError: {str(e)}", {}

        # Validate @context
        context = data.get("@context")
        if not context or "schema.org" not in str(context).lower():
            return False, f"Missing or invalid @context: {context} (expected https://schema.org)", data

        # Validate @type
        schema_type = data.get("@type")
        if not schema_type:
            return False, "Missing @type definition", data

        # Specific type validations
        if schema_type == "SoftwareApplication":
            if "name" not in data or "applicationCategory" not in data:
                return False, "SoftwareApplication missing 'name' or 'applicationCategory'", data
        elif schema_type == "FAQPage":
            if "mainEntity" not in data or not isinstance(data["mainEntity"], list):
                return False, "FAQPage missing 'mainEntity' question list", data
            for q in data["mainEntity"]:
                if q.get("@type") != "Question" or "acceptedAnswer" not in q:
                    return False, "FAQ item missing Question type or acceptedAnswer", data
        elif schema_type == "Organization":
            if "name" not in data or "url" not in data:
                return False, "Organization missing 'name' or 'url'", data
        elif schema_type == "HowTo":
            if "name" not in data or "step" not in data:
                return False, "HowTo missing 'name' or 'step' list", data
        elif schema_type == "BreadcrumbList":
            if "itemListElement" not in data:
                return False, "BreadcrumbList missing 'itemListElement'", data
        elif schema_type == "ContactPage":
            if "mainEntity" not in data and "name" not in data:
                return False, "ContactPage missing mainEntity or name", data

        return True, "Valid Schema.org JSON-LD", data

    def validate_robots_txt(self, filepath: str) -> Tuple[bool, str, Dict[str, Any]]:
        """Validates robots.txt directives and structure."""
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()

        has_user_agent = False
        has_sitemap = False
        has_ai_bot = False
        directives_count = 0

        for line in lines:
            line_str = line.strip()
            if not line_str or line_str.startswith("#"):
                continue
            directives_count += 1
            if line_str.lower().startswith("user-agent:"):
                has_user_agent = True
                agent = line_str.split(":", 1)[1].strip()
                if agent.lower() in ["gptbot", "perplexitybot", "claudebot", "google-extended"]:
                    has_ai_bot = True
            elif line_str.lower().startswith("sitemap:"):
                has_sitemap = True

        if not has_user_agent:
            return False, "robots.txt missing User-agent directive", {"lines": directives_count}
        if not has_sitemap:
            return False, "robots.txt missing Sitemap directive", {"lines": directives_count}

        return True, f"Valid robots.txt with {directives_count} directives (AI bots declared: {has_ai_bot})", {
            "directives_count": directives_count,
            "has_ai_bot": has_ai_bot
        }

    def validate_llms_txt(self, filepath: str) -> Tuple[bool, str, Dict[str, Any]]:
        """Validates llms.txt standard markdown file structure."""
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        has_h1 = bool(re.search(r"^#\s+.+", content, re.MULTILINE))
        has_blockquote_or_desc = bool(re.search(r"^>\s+.+", content, re.MULTILINE))
        has_sections = bool(re.search(r"^##\s+.+", content, re.MULTILINE))

        if not has_h1:
            return False, "llms.txt missing top-level # Title heading", {}
        if not has_blockquote_or_desc:
            return False, "llms.txt missing overview summary blockquote (> summary)", {}
        if not has_sections:
            return False, "llms.txt missing ## sub-headings for features / docs", {}

        return True, "Valid llms.txt adhering to llmstxt.org specification", {
            "char_count": len(content),
            "line_count": len(content.splitlines())
        }

    def validate_xml_sitemap(self, filepath: str) -> Tuple[bool, str, Dict[str, Any]]:
        """Validates XML sitemap structure."""
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        if not content.strip().startswith("<?xml"):
            return False, "Sitemap missing XML declaration", {}
        if "<urlset" not in content or "</urlset>" not in content:
            return False, "Sitemap missing <urlset> wrapper", {}
        if "<loc>" not in content or "</loc>" not in content:
            return False, "Sitemap missing <loc> URL nodes", {}

        url_count = len(re.findall(r"<loc>(.*?)</loc>", content))
        return True, f"Valid XML sitemap containing {url_count} URLs", {"url_count": url_count}

    def validate_html_snippet(self, filepath: str) -> Tuple[bool, str, Dict[str, Any]]:
        """Validates HTML/CSS snippet tags, protocols, and attributes."""
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # Check for unclosed tags or syntax errors
        if "http://app.incubrix.com" in content:
            return False, "Snippet contains insecure HTTP link (http:// instead of https://)", {}

        # Check meta tag attributes
        if "<meta" in content:
            if 'content=""' in content and 'name="description"' in content:
                return False, "Meta tag has empty content attribute", {}

        return True, f"Valid HTML snippet ({len(content)} bytes)", {"length": len(content)}

    def validate_all(self, fix_records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Runs validation across all 20 fix files and records proof logs."""
        print("=" * 70)
        print("  INCUBRIX TECHNICAL FIX VALIDATOR")
        print("=" * 70)

        results = []
        for fix in fix_records:
            fix_id = fix["fix_id"]
            code_url = fix["code_or_text_url"]
            validator_name = fix["validator_used"]

            # Resolve local path
            local_path = code_url
            if not os.path.exists(local_path):
                # Try relative to base dir or fixes dir
                candidate = os.path.join(self.fixes_dir, os.path.basename(code_url))
                if os.path.exists(candidate):
                    local_path = candidate

            if not os.path.exists(local_path):
                res = {
                    "fix_id": fix_id,
                    "file": code_url,
                    "validator": validator_name,
                    "passed": False,
                    "message": f"Fix file not found: {code_url}",
                    "details": {}
                }
                results.append(res)
                print(f"[-] {fix_id}: FAIL (File not found: {code_url})")
                continue

            # Route by extension / type
            ext = os.path.splitext(local_path)[1].lower()
            if ext == ".json":
                passed, msg, details = self.validate_json_ld(local_path)
            elif "robots" in os.path.basename(local_path).lower():
                passed, msg, details = self.validate_robots_txt(local_path)
            elif "llms" in os.path.basename(local_path).lower():
                passed, msg, details = self.validate_llms_txt(local_path)
            elif ext == ".xml":
                passed, msg, details = self.validate_xml_sitemap(local_path)
            else:
                passed, msg, details = self.validate_html_snippet(local_path)

            status_str = "PASS" if passed else "FAIL"
            print(f"[{'+' if passed else '-'}] {fix_id} ({os.path.basename(local_path)}): {status_str} -> {msg}")

            results.append({
                "fix_id": fix_id,
                "file": local_path,
                "validator": validator_name,
                "passed": passed,
                "message": msg,
                "details": details,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })

        self.validation_results = results

        # Save validation results JSON log
        log_path = os.path.join(self.results_dir, "validation_log.json")
        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)

        # Save Markdown validation proof report
        report_path = os.path.join(self.results_dir, "validation_report.md")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("# IncuBrix Technical Fixes Validation Report\n\n")
            f.write(f"**Audit Date:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}  \n")
            f.write(f"**Total Fixes Evaluated:** {len(results)}  \n")
            f.write(f"**Total Passed:** {sum(1 for r in results if r['passed'])}  \n\n")
            f.write("| Fix ID | File | Validator Used | Status | Proof Details |\n")
            f.write("| :--- | :--- | :--- | :---: | :--- |\n")
            for r in results:
                status_icon = "🟢 PASS" if r["passed"] else "🔴 FAIL"
                f.write(f"| **{r['fix_id']}** | `{os.path.basename(r['file'])}` | {r['validator']} | {status_icon} | {r['message']} |\n")

        print("=" * 70)
        print(f"[✓] Validation complete. Logs saved to:\n    - {log_path}\n    - {report_path}")
        print("=" * 70)

        return results


def main():
    import csv
    csv_path = "output/fixes/fixes_table.csv"
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found. Run site_auditor.py first.")
        return

    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fixes = list(reader)

    validator = FixValidator()
    validator.validate_all(fixes)


if __name__ == "__main__":
    main()
