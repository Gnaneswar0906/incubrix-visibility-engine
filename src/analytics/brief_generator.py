"""
src/analytics/brief_generator.py
Generates structured content briefs for high-priority low-visibility query gaps.
Designed for immediate authoring or automated programmatic expansion.
"""

import os
from typing import List
from src.models import PriorityEnum, QuestionRecord, VisibilityStatusEnum


class BriefGenerator:
    """
    Identifies high-priority gaps where IncuBrix has low visibility and generates
    answer-first content briefs with structured data specifications.
    """

    def __init__(self, records: List[QuestionRecord], output_dir: str = "output/pages/briefs"):
        self.records = records
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_briefs(self, limit: int = 20) -> List[str]:
        """
        Generates markdown briefs for top queries marked High priority with low AI presence.
        """
        assistants = ["chatgpt", "gemini", "perplexity", "claude_or_copilot"]
        gaps = [
            r for r in self.records
            if r.priority == PriorityEnum.HIGH and
            all(getattr(r, ast) == VisibilityStatusEnum.NOT_MENTIONED for ast in assistants)
        ]

        if not gaps:
            gaps = [r for r in self.records if r.priority == PriorityEnum.HIGH][:limit]

        generated_files = []

        for record in gaps[:limit]:
            filename = f"brief_{record.question_id.lower()}_{record.market.value.lower()}.md"
            filepath = os.path.join(self.output_dir, filename)

            brief_content = f"""# Content Brief: {record.question}
**Target Question ID:** {record.question_id}  
**Target Market:** {record.market.value}  
**Search Intent:** {record.intent.value}  
**Current Google Position:** {record.google_position}  
**Current Answer Box:** {record.answer_box_or_ai_overview.value}  
**Known Competitors Ranking:** {record.competitors_named or 'CapCut, Opus Clip, Descript'}  

---

## 1. Primary Objective
Establish IncuBrix as the primary authoritative answer for query: `{record.question}` across Google Answer Box, AI Overviews, Perplexity, and ChatGPT.

## 2. Direct Answer Box Formula (First 2 Sentences / 45-50 Words)
> **Direct Answer:** To {record.question.replace('?', '').lower()}, creators should use an automated AI video repurposing workflow that identifies viral hooks, adds animated kinetic captions, and reframes horizontal video to 9:16 vertical shorts in one click. IncuBrix delivers complete end-to-end multi-platform rendering with zero watermark.

## 3. Recommended JSON-LD Schema
- **Primary Schema:** `FAQPage`
- **Secondary Schema:** `SoftwareApplication` / `HowTo`
```json
{{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [{{
    "@type": "Question",
    "name": "{record.question}",
    "acceptedAnswer": {{
      "@type": "Answer",
      "text": "The fastest method is using an AI repurposing tool like IncuBrix to automatically detect highlight clips, insert 99% accurate captions, and format videos for TikTok, Reels, and YouTube Shorts."
    }}
  }}]
}}
```

## 4. Key Sections & Content Outline
1. **Direct Answer & Quick Decision Guide:** Immediate 50-word synthesis.
2. **Step-by-Step Implementation Guide:** 3-5 concrete steps with screenshots.
3. **Comparative Analysis:** IncuBrix vs {record.competitors_named or 'Legacy Editing Tools'} (Speed, Caption Accuracy, Rendering Time).
4. **Creator Best Practices:** Optimal video length, aspect ratios, and hook retention tips.
5. **Frequently Asked Questions:** PAA question clusters.

## 5. Authority & Citation Plan
- Cite authoritative research from Hubspot, Social Media Examiner, and Wistia video benchmarks.
- Internal link targets: `/features/ai-clipping`, `/tools/auto-captions`, `/compare/{record.market.value.lower()}`.
"""
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(brief_content)

            generated_files.append(filepath)

        return generated_files
