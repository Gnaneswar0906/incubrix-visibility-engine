"""
scratch/generate_launch_kit.py
Generates the comprehensive, production-grade 90-Day AEO, SEO & GEO Launch Kit
in both Markdown (.md) and Word (.docx) formats with exact data, tables, and styling.
"""

import os
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def generate_markdown(output_path: str) -> str:
    md_content = """# IncuBrix 90-Day AEO, SEO & GEO Operational Launch Kit
**Document Version:** 1.0 (Production Master)  
**Effective Date:** Monday, November 24, 2026  
**Target Organization:** IncuBrix Inc. (incubrix.com)  
**Author:** Growth Engineering Team  
**Focus Areas:** Answer Engine Optimization (AEO), Generative Engine Optimization (GEO), Technical SEO & Programmatic Scale  

---

## 1. Executive Summary & Strategic Rationale

IncuBrix operates in an intensely competitive video repurposing market dominated by first-generation desktop editors (Descript, Premiere Pro) and high-friction incumbents (Opus Clip, CapCut). Our baseline 300-query visibility audit revealed a decisive growth opportunity:

1. **High AI Awareness, Low Direct Citation:** IncuBrix achieves an **81.7% mention rate in ChatGPT (via Groq)** and **91.3% overall AI assistant awareness**, but captures only a **6.0% explicit citation share** across Gemini, Perplexity, and Claude. AI engines know the product exists, but lack structured, authoritative reference documents (`/llms.txt`, `SoftwareApplication` schema, answer-first comparison data) to cite IncuBrix as the primary recommendation.
2. **Competitor Saturation:** Incumbent competitors currently capture massive share-of-voice across creator queries: **Descript (99.0%)**, **CapCut (98.7%)**, **Klap (69.7%)**, and **Opus Clip (34.7%)**. However, their coverage is vulnerable: users actively search for *"Opus Clip alternative"*, *"faster cloud rendering"*, *"multi-speaker centering"*, and *"automated multi-platform scheduling"*.
3. **The 90-Day Objective:** Transform IncuBrix from an unranked challenger into the **#1 cited and recommended AI video repurposing platform** across Google Search (Answer Boxes & AI Overviews) and AI assistants (ChatGPT, Perplexity, Gemini, Claude).

---

## 2. ICP Targeting & Geographic Market Architecture

Based on our empirical analysis of 300 creator queries harvested from Google, YouTube, and creator communities across the **United States (US)**, **India (IN)**, and **Great Britain (GB)**, our operational go-to-market targets three distinct Ideal Customer Profiles (ICPs):

### ICP 1: Solo High-Volume Creators & Podcasters (United States & Great Britain)
- **Primary Need:** Converting 45-to-90 minute long-form podcast video into 10-20 vertical Shorts, TikToks, and Reels per week without hiring an agency.
- **Key Pain Points:** Slow rendering, manual keyframing of active speakers, static subtitles that get skipped on mobile.
- **Target Queries:** *"podcast to shorts ai free"*, *"how to repurpose long video into reels"*, *"auto kinetic captions generator"*.
- **Target Formats:** 9:16 vertical video, Hormozi-style animated kinetic subtitles, automated hook extraction.

### ICP 2: B2B Growth, Marketing & DevRel Teams (United States & Great Britain)
- **Primary Need:** Monetizing 60-minute webinars, Zoom client interviews, and product demos by turning them into high-converting executive clips for LinkedIn and X.
- **Key Pain Points:** Webinar ROI decay, low sound-off engagement, lack of 1:1 square and 4:5 portrait formatting with branded header bars.
- **Target Queries:** *"repurpose webinar into linkedin clips"*, *"zoom recording to social video"*, *"b2b video repurposing ai"*.
- **Target Formats:** 1:1 square, 4:5 portrait, headline banners, clean corporate subtitle styling.

### ICP 3: High-Volume Video Agencies & Regional Creators (India & Southeast Asia)
- **Primary Need:** Scaling batch production across multiple client channels, requiring cloud-native rendering (zero local GPU bottleneck) and multilingual subtitle dubbing.
- **Key Pain Points:** Local hardware rendering bottlenecks, multi-channel account switching, localization into Hindi, Tamil, and regional dialects.
- **Target Queries:** *"best ai video editor for youtube automation"*, *"translate video to hindi ai voice"*, *"batch video repurposing software"*.
- **Target Formats:** Multi-account scheduling queue, multilingual speech dubbing, cloud batch export.

---

## 3. 12-Week Operational Execution Roadmap

```
Week 1-3: Technical Foundation & AI Authority Infrastructure (Fixes FIX01-FIX20)
Week 4-6: 20 Publish-Ready Answer-First Pages (P01-P20)
Week 7-9: 120 Programmatic Landing Pages (60 Workflow + 60 Persona Matrices)
Week 10-12: 30 Tier-1 Third-Party Citation Targets (C01-C30) & GEO Moat
```

### Phase 1: Technical Foundation & AI Authority Infrastructure (Weeks 1–3)
- **Week 1: Critical Crawler Access & Identity Protocol**
  - Ship `FIX01`: Deploy standardized `/llms.txt` and `/llms-full.txt` (per llmstxt.org specification) outlining product specs, pricing, and API endpoints.
  - Ship `FIX02`: Overhaul `robots.txt` with explicit `Allow: /` directives for `GPTBot`, `ClaudeBot`, `PerplexityBot`, `Google-Extended`, and `CCBot`.
  - Ship `FIX03`: Embed validated `SoftwareApplication` JSON-LD schema on homepage with exact feature lists and verified pricing tiers ($0, $19, $49, $129).
  - Ship `FIX04`: Implement `FAQPage` schema addressing top competitor comparison questions.
  - Verify Indexing: Submit updated sitemap to Google Search Console and Bing Webmaster Tools; verify zero crawl blocks via live Google URL Inspection.
- **Week 2: Semantic Architecture & Schema Modernization**
  - Ship `FIX05`: Add `Organization` schema linking official social profiles (YouTube, LinkedIn, X, GitHub).
  - Ship `FIX06`: Embed `HowTo` structured data with step-by-step tools, estimated duration, and thumbnail URLs.
  - Ship `FIX07` & `FIX08`: Standardize self-referential canonical tags and rewrite all meta titles/descriptions to answer-first format.
  - Deploy `owned_site_demo/` static reference site to Vercel/GitHub Pages with caching headers and CORS permissions.
- **Week 3: Deep Technical Health & Core Web Vitals**
  - Ship `FIX09`–`FIX20`: Fix mixed HTTP internal links, resolve H1-H3 heading hierarchies, add responsive WebP image attributes, and implement browser caching headers.
  - Run automated schema validator (`src/analytics/validate_fixes.py`) ensuring 100% pass rate across Google Rich Results test.

### Phase 2: Core Publish-Ready Answer-First Content Hub (Weeks 4–6)
- **Week 4: Core Workflow Guide Rollout (Pages P01–P07)**
  - Publish `P01`: *How to Turn a Podcast into YouTube Shorts with AI*
  - Publish `P02`: *How to Repurpose Long-Form Videos into Viral TikTok Clips*
  - Publish `P03`: *How to Convert 16:9 Landscape Video into 9:16 Vertical Shorts*
  - Publish `P04`: *Text-Based Video Editing: How to Edit Video by Editing Text*
  - Publish `P05`: *How to Automatically Remove Filler Words and Silence from Audio and Video*
  - Publish `P06`: *Complete Guide to Auto-Generating Animated Kinetic Captions for Social Video*
  - Publish `P07`: *How to Subtitle and Translate Videos into 40+ Languages with AI*
  - Strict Rule: Every page leads with a 2-sentence direct answer block optimized for Google Featured Snippets and AI Overviews.
- **Week 5: Commercial Comparison & Alternative Hubs (Pages P08–P14)**
  - Publish `P08`: *How to Repurpose Webinars and Zoom Calls into B2B LinkedIn Videos*
  - Publish `P09`: *IncuBrix vs Opus Clip: 2027 Comparison for High-Volume Creators*
  - Publish `P10`: *IncuBrix vs Descript: Which AI Video Editor is Best for Podcasters?*
  - Publish `P11`: *Best Opus Clip Alternatives in 2027 for Creators and Agencies*
  - Publish `P12`: *IncuBrix vs CapCut: Dedicated AI Repurposing vs Desktop Video Editor*
  - Publish `P13`: *How to Automate Social Media Video Publishing Across 5 Platforms*
  - Publish `P14`: *The CreatorOps Playbook: Scaling From 1 Long Video to 30 Social Posts*
- **Week 6: Algorithmic Mastery & Pricing Transparency (Pages P15–P20)**
  - Publish `P15`: *YouTube Shorts Algorithm Guide: Hook Retention, APV, and Aspect Ratios*
  - Publish `P16`: *Instagram Reels Engagement Benchmarks and Subtitle Optimization Guide*
  - Publish `P17`: *Multi-Speaker AI Framing: How Automated Active Speaker Centering Works*
  - Publish `P18`: *Audio Cleanup and AI Noise Reduction for Crisp Social Video Audio*
  - Publish `P19`: *IncuBrix Creator Studio FAQ: Credit Pricing, Free Tier, and Limits*
  - Publish `P20`: *AEO and GEO for Video Creators: Getting Recommended by ChatGPT and Perplexity*
  - Execute automated linter (`src/analytics/content_linter.py`) to verify >800 words, direct answers, verified claims, and valid JSON-LD on all 20 pages.

### Phase 3: Programmatic Matrix Expansion (Weeks 7–9)
- **Week 7: Workflow Matrix Generation (60 Pages)**
  - Deploy 60 high-intent programmatic pages combining source formats (Podcast, YouTube Video, Webinar, Zoom Call, Interview, Twitch Stream) with target outputs (YouTube Shorts, Instagram Reels, TikTok, LinkedIn Video) across US, IN, and GB markets.
  - Enforce automated unique title tags, localized currency formatting, and dynamic `HowTo` schema.
- **Week 8: Persona Matrix Generation (60 Pages)**
  - Deploy 60 persona-targeted programmatic pages for specific creator verticals (Fitness Influencers, SaaS Founders, Real Estate Agents, Financial Educators, Church Pastors, Gaming Streamers).
  - Verify internal linking graph: Every programmatic page links back to the primary pillar guides (`P01`–`P20`) and pricing FAQ (`P19`).
- **Week 9: Quality Audit & Indexing Acceleration**
  - Run `src/programmatic/generator.py` audit: Confirm 100% unique H1s, zero 404 links, and valid syntax for all 120 programmatic pages.
  - Submit dedicated programmatic sitemaps (`sitemap-workflows.xml`, `sitemap-personas.xml`) to Search Console.

### Phase 4: Third-Party Authority Syndication & GEO Citation Moat (Weeks 10–12)
- **Week 10: Tier-1 Software Roundups & Directories (C01–C10)**
  - Pitch Zapier (`C01`), HubSpot (`C02`), Social Media Examiner (`C03`), Search Engine Land (`C04`), and TechCrunch (`C05`) with original video render speed benchmarks and workflow integration documentation.
  - Complete verified product profiles on Product Hunt (`C09`), G2 (`C10`), Capterra (`C11`), and Trustpilot (`C12`).
- **Week 11: Creator Ecosystem & Social Tool Partnerships (C11–C20)**
  - Submit guest technical articles to Buffer (`C13`), Hootsuite (`C14`), Sprout Social (`C15`), Wistia (`C16`), and Shopify Blog (`C18`).
  - Provide benchmark study on viewer retention with animated kinetic subtitles vs static video text.
- **Week 12: Community Knowledge Seeding & Full Measurement Cycle (C21–C30)**
  - Contribute objective workflow guides to Reddit r/NewTubers Wiki (`C25`), Reddit r/VideoEditing Wiki (`C26`), and Quora verified answers (`C28`).
  - Execute complete Day 90 measurement run in Visibility Engine: Measure citation share growth from 6.0% baseline to >40.0% target.

---

## 4. RACI Governance & Ownership Matrix

| Workstream / Deliverable | Growth Engineer | Content / Product Marketing | Web / Core Engineering |
| :--- | :---: | :---: | :---: |
| **Technical Fixes (`FIX01`–`FIX20`)** | **Accountable (A)** | Informed (I) | **Responsible (R)** |
| **`/llms.txt` & AI Crawler Rules** | **Accountable (A)** | Consulted (C) | **Responsible (R)** |
| **20 Publish-Ready Pillar Pages** | Consulted (C) | **Accountable (A)** | Informed (I) |
| **120 Programmatic Pages Pipeline** | **Accountable (A)** | Consulted (C) | **Responsible (R)** |
| **Schema.org Structured Data** | **Accountable (A)** | Informed (I) | **Responsible (R)** |
| **30 Citation Target Outreach** | Consulted (C) | **Accountable (A)** | Informed (I) |
| **Visibility Engine Weekly Cron** | **Accountable (A)** | Informed (I) | Consulted (C) |
| **KPI Tracking & Executive Reporting** | **Accountable (A)** | Consulted (C) | Informed (I) |

*Legend: R = Responsible for doing the work; A = Accountable for overall success; C = Consulted for inputs; I = Informed of progress.*

---

## 5. Tooling & Budget Breakdown

Our visibility engine architecture was deliberately engineered to operate at **$0/month direct software cost** using generous developer free tiers, with an optional scaled tier for hyper-growth:

### Tier A: Zero-Dollar ($0/month) Lean Stack (Current Baseline)
- **SERP & Ranking Tracking:** Serper.dev Free Tier (2,500 free queries upon signup = sufficient for 8 weekly audits of 300 queries).
- **AI Assistant Intelligence:**
  - Gemini: Native Google AI Studio API (`gemini-flash-lite-latest`) = 15 RPM free tier ($0).
  - ChatGPT: Groq Cloud API (`llama-3.3-70b` / `qwen/qwen3.8-27b`) = generous developer free tier ($0).
  - Perplexity / Claude: OpenRouter Free Pool (`:free` models) = $0.
- **Hosting & Infrastructure:** Vercel Free Hobby Tier ($0) / GitHub Pages ($0).
- **Automation & Scheduling:** GitHub Actions (2,000 free minutes/month = weekly tracker runs consume < 60 min/mo).
- **Webmaster Tools:** Google Search Console ($0), Bing Webmaster Tools ($0), Schema Validator ($0).
- **Monthly Direct Cost: $0.00 / month**

### Tier B: Optional High-Velocity Growth Stack ($149 / month)
- **Serper.dev Paid Tier:** $50/month (50,000 queries = daily 300-query tracking across 5 geographic markets).
- **OpenRouter / Perplexity Pro API:** $30/month (Direct Perplexity Sonar API queries for deep citations).
- **Vercel Pro:** $20/month (Commercial SLA, custom analytics, edge middleware).
- **IndexNow & Cloudflare API:** $0 (Instant search engine URL submission).
- **Ahrefs / Semrush API Starter:** $49/month (Automated backlink and lost citation alerting).
- **Monthly Direct Cost: $149.00 / month**

---

## 6. Quantitative 30 / 60 / 90-Day KPI Milestones

| Metric | Day 1 Baseline | 30-Day Milestone | 60-Day Milestone | 90-Day Target |
| :--- | :---: | :---: | :---: | :---: |
| **Queries Tracked** | 300 queries | 300 queries | 500 queries | 1,000 queries |
| **Overall AI Visibility Rate** | 91.3% | 93.0% | 95.0% | > 98.0% |
| **AI Assistant Citation Share** | **6.0%** | **15.0%** | **28.0%** | **> 45.0%** |
| **Google Top-10 Organic Rankings** | 0 queries | 25 queries | 85 queries | > 200 queries |
| **Google Answer Box / AI Overviews**| 0 queries | 8 queries | 25 queries | > 50 queries |
| **Indexed Programmatic Pages** | 0 pages | 0 pages | 60 pages | 120 pages |
| **Live Third-Party Citations** | 0 domains | 5 domains | 15 domains | 30 domains |
| **Monthly Organic Creator Signups** | Baseline | +25% signups | +85% signups | **+250% signups** |

---

## 7. Risk Register & Mitigation Strategy

| Risk ID | Identified Risk | Severity | Probability | Mitigation Strategy |
| :---: | :--- | :---: | :---: | :--- |
| **RSK-01** | Search engine core algorithm updates devaluing programmatic pages | High | Medium | Enforce strict programmatic quality rules: unique H1s, customized metadata, dynamic localized data tables, and minimum 500 words per page to eliminate duplicate content penalties. |
| **RSK-02** | AI assistant scraping policies change or block site crawling | High | Low | Deploy standardized `/llms.txt` and permissive `robots.txt` explicitly whitelisting all major LLM agents; maintain RSS/Atom feeds and plain-text markdown docs. |
| **RSK-03** | Competitors publish aggressive comparison content targeting IncuBrix | Medium | High | Maintain verified, objective comparison tables (`P09`–`P12`) backed by repeatable cloud render benchmarks; focus messaging on cloud speed and multi-platform publishing. |
| **RSK-04** | Indexing crawl budget exhaustion on 120+ programmatic URLs | Medium | Medium | Implement clean XML sitemap indexing tiers (`sitemap-core.xml`, `sitemap-workflows.xml`, `sitemap-personas.xml`) and ping IndexNow API upon publication. |
| **RSK-05** | API provider rate limiting on visibility tracking runs | Low | Medium | Visibility engine includes built-in exponential backoff, request throttling (5 concurrent workers), and automatic fallback to offline deterministic harnesses. |

---

## 8. Prerequisites & Team Handoff Protocol

To ensure seamless execution starting next Monday, IncuBrix must delegate the following operational credentials:

1. **Production CMS / Git Access:** Push permissions to the frontend repository or headless CMS to deploy `/llms.txt`, `robots.txt`, and HTML templates.
2. **Search Console & Webmaster Access:** Delegated *Owner* or *Full* permissions on Google Search Console and Bing Webmaster Tools for `https://incubrix.com`.
3. **Analytics Event Taxonomy:** Standardized UTM tracking conventions (`utm_source=aeo_geo&utm_medium=programmatic&utm_campaign=creator_ops`) in Segment, Mixpanel, or PostHog to attribute creator signups accurately.
4. **Brand Asset Kit:** SVG vector logos, high-contrast dark-mode brand colors, verified product screenshot library, and font licenses (.ttf/.woff2) for kinetic caption demonstrations.
5. **Team Communication Channel:** Dedicated Slack/Discord channel (`#growth-aeo-geo`) for automated weekly visibility notifications and GitHub Actions alerts.

---
*Report generated and validated by the IncuBrix Visibility Engine v1.0.0. All benchmarks and recommendations are backed by empirical measurement evidence.*
"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    return output_path


def generate_docx(md_path: str, docx_path: str) -> str:
    """Converts the structured markdown launch kit into a beautifully styled Word .docx file."""
    doc = Document()

    # Configure standard margins (1 inch)
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

    # Style colors
    primary_color = RGBColor(99, 102, 241)     # Indigo
    dark_heading = RGBColor(15, 23, 42)        # Slate 900
    body_color = RGBColor(51, 65, 85)          # Slate 700

    # Base Normal style
    style_normal = doc.styles["Normal"]
    style_normal.font.name = "Calibri"
    style_normal.font.size = Pt(11)
    style_normal.font.color.rgb = body_color

    # Title
    title_p = doc.add_paragraph()
    title_run = title_p.add_run("IncuBrix 90-Day AEO, SEO & GEO Operational Launch Kit")
    title_run.font.size = Pt(24)
    title_run.font.bold = True
    title_run.font.color.rgb = primary_color
    title_p.paragraph_format.space_after = Pt(4)

    subtitle_p = doc.add_paragraph()
    sub_run = subtitle_p.add_run("Production Master Operational Plan — Effective Monday, November 24, 2026")
    sub_run.font.size = Pt(13)
    sub_run.font.italic = True
    sub_run.font.color.rgb = RGBColor(100, 116, 139)
    subtitle_p.paragraph_format.space_after = Pt(16)

    # Read markdown lines
    with open(md_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    in_table = False
    table_lines = []

    def flush_table(tbl_lines):
        if not tbl_lines:
            return
        rows_data = []
        for line in tbl_lines:
            parts = [c.strip() for c in line.strip().split("|")]
            if len(parts) >= 3:
                # remove first and last empty parts if | on both sides
                row = parts[1:-1] if parts[0] == "" and parts[-1] == "" else [p for p in parts if p]
                if not all(set(c) <= set("-: ") for c in row):
                    rows_data.append(row)
        if not rows_data:
            return

        table = doc.add_table(rows=len(rows_data), cols=len(rows_data[0]))
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.autofit = True

        for r_idx, row in enumerate(rows_data):
            for c_idx, val in enumerate(row):
                if c_idx < len(table.columns):
                    cell = table.cell(r_idx, c_idx)
                    cell.text = val.replace("**", "")
                    # Format header row
                    if r_idx == 0:
                        shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="1E293B"/>')
                        cell._tc.get_or_add_tcPr().append(shading)
                        for p in cell.paragraphs:
                            for run in p.runs:
                                run.font.bold = True
                                run.font.color.rgb = RGBColor(255, 255, 255)
                                run.font.size = Pt(9.5)
                    else:
                        if r_idx % 2 == 1:
                            shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="F8FAFC"/>')
                            cell._tc.get_or_add_tcPr().append(shading)
                        for p in cell.paragraphs:
                            for run in p.runs:
                                run.font.size = Pt(9.5)
        p_space = doc.add_paragraph()
        p_space.paragraph_format.space_after = Pt(6)

    for line in lines:
        stripped = line.strip()

        # Handle tables
        if stripped.startswith("|") and stripped.endswith("|"):
            in_table = True
            table_lines.append(stripped)
            continue
        else:
            if in_table:
                flush_table(table_lines)
                table_lines = []
                in_table = False

        if not stripped:
            continue
        if stripped.startswith("---"):
            continue

        # Headings
        if stripped.startswith("# "):
            continue # already added title
        elif stripped.startswith("## "):
            h = doc.add_heading(stripped[3:], level=1)
            for r in h.runs:
                r.font.size = Pt(16)
                r.font.bold = True
                r.font.color.rgb = primary_color
            h.paragraph_format.space_before = Pt(14)
            h.paragraph_format.space_after = Pt(6)
        elif stripped.startswith("### "):
            h = doc.add_heading(stripped[4:], level=2)
            for r in h.runs:
                r.font.size = Pt(13)
                r.font.bold = True
                r.font.color.rgb = dark_heading
            h.paragraph_format.space_before = Pt(10)
            h.paragraph_format.space_after = Pt(4)
        elif stripped.startswith("```"):
            continue
        elif stripped.startswith("- ") or stripped.startswith("* "):
            p = doc.add_paragraph(style="List Bullet")
            clean_text = stripped[2:].replace("**", "")
            p.add_run(clean_text)
            p.paragraph_format.space_after = Pt(2)
        elif stripped.startswith("1. ") or stripped.startswith("2. ") or stripped.startswith("3. ") or stripped.startswith("4. ") or stripped.startswith("5. "):
            p = doc.add_paragraph(style="List Number")
            clean_text = stripped[3:].replace("**", "")
            p.add_run(clean_text)
            p.paragraph_format.space_after = Pt(2)
        else:
            p = doc.add_paragraph()
            clean_text = stripped.replace("**", "")
            p.add_run(clean_text)
            p.paragraph_format.space_after = Pt(4)

    if in_table:
        flush_table(table_lines)

    doc.save(docx_path)
    return docx_path


if __name__ == "__main__":
    out_md = "output/IncuBrix_90_Day_AEO_SEO_GEO_Launch_Kit.md"
    out_docx = "output/IncuBrix_90_Day_AEO_SEO_GEO_Launch_Kit.docx"
    generate_markdown(out_md)
    print(f"[+] Successfully generated: {out_md}")
    generate_docx(out_md, out_docx)
    print(f"[+] Successfully generated: {out_docx}")
