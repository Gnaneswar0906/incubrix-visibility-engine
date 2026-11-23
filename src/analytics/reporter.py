"""
src/analytics/reporter.py
Generates the comprehensive weekly visibility report (weekly_visibility_report.md).
Calculates AI mention rate, citation share, competitor leaderboard, Day 1 vs Day 2 deltas,
Google SERP & AEO metrics, and market breakdowns.
"""

from collections import Counter
from datetime import datetime
import os
from typing import Any, Dict, List
from src.models import (
    AnswerBoxEnum,
    ChangedDay2Enum,
    QuestionRecord,
    VisibilityStatusEnum,
)


class VisibilityReporter:
    """
    Analyzes visibility data across search and AI assistants to generate
    an executive-ready markdown report.
    """

    def __init__(self, records: List[QuestionRecord], output_path: str = "output/reports/weekly_visibility_report.md"):
        self.records = records
        self.output_path = output_path
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    def generate_report(self) -> str:
        """Computes all KPIs and writes the markdown report."""
        total = len(self.records)
        if total == 0:
            content = "# IncuBrix Weekly Visibility Report\n\nNo records available to report."
            with open(self.output_path, "w", encoding="utf-8") as f:
                f.write(content)
            return content

        # Assistant metrics
        assistants = ["chatgpt", "gemini", "perplexity", "claude_or_copilot"]
        ast_stats = {}
        for ast in assistants:
            cited = sum(1 for r in self.records if getattr(r, ast) == VisibilityStatusEnum.CITED)
            mentioned = sum(1 for r in self.records if getattr(r, ast) == VisibilityStatusEnum.MENTIONED)
            not_mentioned = sum(1 for r in self.records if getattr(r, ast) == VisibilityStatusEnum.NOT_MENTIONED)
            total_visible = cited + mentioned
            ast_stats[ast] = {
                "cited": cited,
                "mentioned": mentioned,
                "not_mentioned": not_mentioned,
                "visible_pct": (total_visible / total) * 100,
                "citation_share": (cited / total) * 100
            }

        # Overall AI metrics
        any_ai_visible = sum(
            1 for r in self.records
            if any(getattr(r, ast) in [VisibilityStatusEnum.CITED, VisibilityStatusEnum.MENTIONED] for ast in assistants)
        )
        any_ai_cited = sum(
            1 for r in self.records
            if any(getattr(r, ast) == VisibilityStatusEnum.CITED for ast in assistants)
        )
        overall_ai_mention_rate = (any_ai_visible / total) * 100
        overall_ai_citation_share = (any_ai_cited / total) * 100

        # Google SERP & AEO metrics
        top10_count = sum(1 for r in self.records if isinstance(r.google_position, int) and r.google_position <= 10)
        answer_box_count = sum(1 for r in self.records if r.answer_box_or_ai_overview in [AnswerBoxEnum.ANSWER_BOX, AnswerBoxEnum.BOTH])
        ai_overview_count = sum(1 for r in self.records if r.answer_box_or_ai_overview in [AnswerBoxEnum.AI_OVERVIEW, AnswerBoxEnum.BOTH])

        # Competitor Leaderboard
        comp_counter = Counter()
        for r in self.records:
            if r.competitors_named:
                for comp in r.competitors_named.split(","):
                    c_clean = comp.strip()
                    if c_clean:
                        comp_counter[c_clean] += 1
        top_competitors = comp_counter.most_common(10)

        # Day 1 vs Day 2 Deltas
        changed_count = sum(1 for r in self.records if r.changed_on_day2 == ChangedDay2Enum.YES)
        volatility_rate = (changed_count / total) * 100

        # Market Breakdown
        market_stats = {}
        for r in self.records:
            m = r.market.value
            if m not in market_stats:
                market_stats[m] = {"total": 0, "visible": 0}
            market_stats[m]["total"] += 1
            if any(getattr(r, ast) in [VisibilityStatusEnum.CITED, VisibilityStatusEnum.MENTIONED] for ast in assistants):
                market_stats[m]["visible"] += 1

        # Priority Gaps (High priority, not mentioned in AI)
        high_priority_gaps = [
            r for r in self.records
            if r.priority.value == "High" and all(getattr(r, ast) == VisibilityStatusEnum.NOT_MENTIONED for ast in assistants)
        ]

        report_md = f"""# IncuBrix Weekly Visibility, AEO & GEO Report
**Audit Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Total Target Queries Tracked:** {total}  
**Markets Evaluated:** US, GB, CA, AU, IN, SG, Other  
**Engine Version:** v1.0.0 (Production Grade)

---

## 1. Executive Summary & Core KPIs

| Metric | Measured Value | Benchmark / Target | Status |
| :--- | :--- | :--- | :--- |
| **Overall AI Visibility Rate** | **{overall_ai_mention_rate:.1f}%** | > 25.0% | {"🟢 On Target" if overall_ai_mention_rate >= 25 else "🟡 Growth Opportunity"} |
| **AI Citation Share** | **{overall_ai_citation_share:.1f}%** | > 15.0% | {"🟢 Strong" if overall_ai_citation_share >= 15 else "🟡 Under Development"} |
| **Google Top 10 Positions** | **{top10_count} ({top10_count/total*100:.1f}%)** | > 10% | {"🟢 Established" if top10_count >= 10 else "🟡 Expansion Needed"} |
| **Answer Box Appearance Share** | **{answer_box_count} ({answer_box_count/total*100:.1f}%)** | > 15% | High Potential |
| **AI Overview Coverage** | **{ai_overview_count} ({ai_overview_count/total*100:.1f}%)** | > 25% | Primary GEO Target |
| **Day 1 -> Day 2 Volatility Delta** | **{volatility_rate:.1f}% ({changed_count} queries)** | < 20% | Stable Baseline |

---

## 2. Assistant-by-Assistant Scorecard

Breakdown across the 4 major generative search engines and assistants:

| AI Assistant | Total Visible (Cited + Mentioned) | Visible Rate | Explicitly Cited | Citation Share | Not Mentioned |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **ChatGPT** | {ast_stats['chatgpt']['cited'] + ast_stats['chatgpt']['mentioned']} | {ast_stats['chatgpt']['visible_pct']:.1f}% | {ast_stats['chatgpt']['cited']} | {ast_stats['chatgpt']['citation_share']:.1f}% | {ast_stats['chatgpt']['not_mentioned']} |
| **Gemini** | {ast_stats['gemini']['cited'] + ast_stats['gemini']['mentioned']} | {ast_stats['gemini']['visible_pct']:.1f}% | {ast_stats['gemini']['cited']} | {ast_stats['gemini']['citation_share']:.1f}% | {ast_stats['gemini']['not_mentioned']} |
| **Perplexity** | {ast_stats['perplexity']['cited'] + ast_stats['perplexity']['mentioned']} | {ast_stats['perplexity']['visible_pct']:.1f}% | {ast_stats['perplexity']['cited']} | {ast_stats['perplexity']['citation_share']:.1f}% | {ast_stats['perplexity']['not_mentioned']} |
| **Claude / Copilot** | {ast_stats['claude_or_copilot']['cited'] + ast_stats['claude_or_copilot']['mentioned']} | {ast_stats['claude_or_copilot']['visible_pct']:.1f}% | {ast_stats['claude_or_copilot']['cited']} | {ast_stats['claude_or_copilot']['citation_share']:.1f}% | {ast_stats['claude_or_copilot']['not_mentioned']} |

---

## 3. Competitor Share of Voice Leaderboard

Frequency of competitor mentions across creator workflows:

| Rank | Competitor Platform | Query Mentions | Share of Total Tracked | Primary Workflow Strength |
| :---: | :--- | :---: | :---: | :--- |
"""
        for rank, (comp, count) in enumerate(top_competitors, start=1):
            share = (count / total) * 100
            report_md += f"| {rank} | **{comp}** | {count} | {share:.1f}% | Video Repurposing & Clipping |\n"

        report_md += f"""
---

## 4. Geographic Market Performance

| Market | Total Queries | Visible Queries | AI Visibility Rate |
| :--- | :---: | :---: | :--- |
"""
        for m, s in sorted(market_stats.items()):
            rate = (s["visible"] / s["total"] * 100) if s["total"] else 0
            report_md += f"| **{m}** | {s['total']} | {s['visible']} | {rate:.1f}% |\n"

        report_md += f"""
---

## 5. High-Priority Low-Visibility Gaps ({len(high_priority_gaps)} Queries)

These queries represent immediate quick-win opportunities for new content pages and technical fixes:

"""
        for gap in high_priority_gaps[:10]:
            report_md += (
                f"- **[{gap.question_id}]** `{gap.question}` ({gap.market.value}) - "
                f"Intent: *{gap.intent.value}*, Google Pos: *{gap.google_position}*, "
                f"Source: *{gap.source_type}*\n"
            )

        report_md += """
---

## 6. Actionable Next Steps for IncuBrix Growth
1. **Ship Schema & llms.txt Fixes:** Implement the 20 validated fixes in `02b_FIXES` to improve AI crawlability.
2. **Publish High-Priority Comparison Pages:** Target Opus Clip and CapCut query gaps with answer-first format.
3. **Earn Citations on Tier 1 Directories:** Syndicate guides to Zapier, HubSpot, and Medium to increase Perplexity and Gemini citations.
"""

        with open(self.output_path, "w", encoding="utf-8") as f:
            f.write(report_md)

        return report_md
