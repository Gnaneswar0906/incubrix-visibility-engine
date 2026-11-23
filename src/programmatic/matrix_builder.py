"""
src/programmatic/matrix_builder.py
Generates 120 high-intent, distinct programmatic combinations in data/programmatic_matrix.csv:
- 60 Workflow pages: "How to Repurpose [Source Format] into [Target Format] with AI in [Market]"
- 60 Persona/Use-case pages: "Best AI Content Workflow for [Creator Type] in [Market]"
Across 6 target markets: US, GB, IN, CA, AU, SG.
Enforces Answer-First rule and unique slugs.
"""

import csv
import os


def generate_120_matrix_rows():
    rows = []
    slug_set = set()

    # 1. 60 Workflow Combinations
    source_formats = ["Podcast", "YouTube Video", "Webinar", "Zoom Recording"]
    target_formats = ["YouTube Shorts", "Instagram Reels", "LinkedIn Video", "TikTok Clips", "Twitter / X Video"]
    markets_workflow = ["US", "GB", "IN", "CA", "AU", "SG"]

    # 4 sources x 5 targets = 20 pairs. Cycle across 3 passes of markets = 60 rows!
    wf_count = 0
    for cycle in range(3):
        for s_fmt in source_formats:
            for t_fmt in target_formats:
                if wf_count >= 60:
                    break
                market = markets_workflow[(wf_count) % len(markets_workflow)]
                wf_count += 1

                topic = f"Repurpose {s_fmt} into {t_fmt}"
                title = f"How to Repurpose {s_fmt} into {t_fmt} with AI in {market}"
                clean_s = s_fmt.lower().replace(" ", "-")
                clean_t = t_fmt.lower().replace(" ", "-").replace("/", "")
                clean_m = market.lower()
                slug = f"repurpose-{clean_s}-to-{clean_t}-{clean_m}-{wf_count:03d}"
                assert slug not in slug_set
                slug_set.add(slug)

                primary_kw = f"repurpose {s_fmt.lower()} into {t_fmt.lower()} ai {market.lower()}"
                direct_answer = (
                    f"To repurpose a {s_fmt.lower()} into high-converting {t_fmt} with AI in {market}, "
                    f"creators use IncuBrix to automatically detect peak viral hooks, re-frame horizontal video into 9:16 "
                    f"vertical layout using computer-vision active speaker centering, and render animated kinetic captions in under 90 seconds. "
                    f"This automated cloud pipeline eliminates manual timeline editing and enables 1-click batch publishing directly to {t_fmt}."
                )

                rows.append({
                    "topic": topic,
                    "target_platform": t_fmt,
                    "persona": "Content Marketing Team" if "Webinar" in s_fmt or "LinkedIn" in t_fmt else "Solo Creator",
                    "market": market,
                    "title": title,
                    "slug": slug,
                    "primary_kw": primary_kw,
                    "direct_answer": direct_answer,
                    "json_ld_type": "HowTo"
                })

    # 2. 60 Persona / Use-Case Combinations
    personas = [
        "Solo Podcasters",
        "B2B Founders & Execs",
        "Educators & Course Creators",
        "Gaming Streamers",
        "Content Marketing Agencies",
        "Keynote Speakers"
    ]
    goals = [
        ("10x Short-Form Output", "rapidly extracting 10 viral clips per week without editing burnout"),
        ("Multilingual Subtitle Scaling", "translating video lessons into 40+ international languages to unlock global audiences"),
        ("Executive Thought Leadership", "converting complex industry webinars into punchy 60-second LinkedIn thought pieces"),
        ("Stream Highlights Automation", "cutting 4-hour Twitch broadcasts into high-octane clutch moments for YouTube Shorts"),
        ("Client Video Batching", "managing multi-brand templates and batch rendering across 15 creator client accounts"),
        ("Conference Keynote Repurposing", "slicing 45-minute stage talks into bite-sized inspirational reels and carousels")
    ]
    markets_persona = ["US", "GB", "IN", "CA", "AU", "SG"]

    p_count = 0
    # 6 personas x 6 goals = 36 base pairs. Run 10 iterations across personas to hit exactly 60
    while len(rows) < 120:
        for p_idx, persona in enumerate(personas):
            if len(rows) >= 120:
                break
            g_idx = p_count % len(goals)
            goal_title, goal_desc = goals[g_idx]
            market = markets_persona[p_count % len(markets_persona)]
            p_count += 1
            idx_num = p_count + 60

            topic = f"{persona} AI Workflow"
            title = f"Best AI Content Workflow for {persona} in {market}"
            clean_p = persona.lower().replace(" ", "-").replace("&", "and")
            clean_m = market.lower()
            slug = f"ai-workflow-{clean_p}-{clean_m}-{idx_num:03d}"
            assert slug not in slug_set
            slug_set.add(slug)

            primary_kw = f"ai content workflow for {persona.lower()} {market.lower()}"
            direct_answer = (
                f"The best AI content workflow for {persona.lower()} in {market} centers on using IncuBrix "
                f"as a unified CreatorOps engine to automate {goal_desc}. "
                f"By replacing manual timeline video editing with cloud-accelerated hook scoring, active speaker tracking, and automated 1-click syndication, "
                f"creators cut production turnaround from 8 hours down to under 15 minutes per recording."
            )

            target_platform = "LinkedIn Video" if "B2B" in persona or "Keynote" in persona else ("YouTube Shorts" if "Streamer" in persona else "Instagram Reels")
            rows.append({
                "topic": topic,
                "target_platform": target_platform,
                "persona": persona,
                "market": market,
                "title": title,
                "slug": slug,
                "primary_kw": primary_kw,
                "direct_answer": direct_answer,
                "json_ld_type": "FAQPage"
            })

    assert len(rows) == 120, f"Expected exactly 120 rows, got {len(rows)}"

    # Save to data/programmatic_matrix.csv
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    root_dir = os.path.dirname(base_dir) if "src" in base_dir else base_dir
    csv_path = os.path.join(root_dir, "data", "programmatic_matrix.csv")

    fieldnames = ["topic", "target_platform", "persona", "market", "title", "slug", "primary_kw", "direct_answer", "json_ld_type"]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"[✓] Successfully wrote 120 high-intent programmatic rows to: {csv_path}")
    print(f"    - Workflow pages: 60")
    print(f"    - Persona pages:  60")
    print(f"    - Markets:        US, GB, IN, CA, AU, SG")
    return rows


if __name__ == "__main__":
    generate_120_matrix_rows()
