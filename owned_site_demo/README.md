# IncuBrix Owned-Site Before-and-After AEO & GEO Verification Site

This directory contains a complete, deployment-ready static website (`owned_site_demo/`) designed to prove AEO (Answer Engine Optimization), SEO, and GEO (Generative Engine Optimization) before-and-after indexing performance for **IncuBrix** (incubrix.com).

## Architecture & Optimization Features
1. **Answer-First Architecture:** Every landing page and workflow guide leads with an unambiguous 2-sentence direct answer optimized for Google Featured Snippets and AI Assistant citations (ChatGPT, Perplexity, Gemini, Claude).
2. **Schema.org Structured Data:**
   - Homepage: Embedded `SoftwareApplication` + `Organization` + `FAQPage` JSON-LD.
   - Guides: Embedded `HowTo` and `Article` JSON-LD detailing step-by-step tools, estimated time, and direct answers.
3. **AI Crawler Transparency:**
   - `/llms.txt`: Standardized text file for LLM scrapers (spec at https://llmstxt.org) containing structured capabilities, pricing tiers, and guide URLs.
   - `/robots.txt`: Permissive directives allowing GPTBot, ClaudeBot, PerplexityBot, and Google-Extended.
   - `/sitemap.xml`: Complete XML sitemap with daily/weekly change frequencies.
4. **Vercel / GitHub Pages Deployment:** Includes `vercel.json` with security headers, CORS headers for `llms.txt`, and clean URL routing.

## Site Structure
```
owned_site_demo/
├── index.html                           # Responsive homepage with SoftwareApplication & FAQ schema
├── robots.txt                           # Explicit AI crawler permissions + llms.txt link
├── llms.txt                             # Machine-readable product specification for LLMs
├── sitemap.xml                          # XML sitemap with 5 workflow guides
├── vercel.json                          # Vercel deployment configuration
├── README.md                            # Verification protocol and test documentation
└── guides/
    ├── guide1_podcast_to_shorts.html    # How to turn podcasts into vertical shorts (HowTo Schema)
    ├── guide2_text_based_editing.html   # Text-based transcript video editing guide (Article Schema)
    ├── guide3_kinetic_captions.html     # Animated kinetic captions guide (HowTo Schema)
    ├── guide4_multilingual_dubbing.html # Multilingual AI dubbing & translation (HowTo Schema)
    └── guide5_webinar_repurposing.html  # B2B webinar repurposing for LinkedIn (HowTo Schema)
```

## 1-Command Deployment Instructions
Deploy to Vercel via CLI or Git:
```bash
# Via Vercel CLI
cd owned_site_demo
npx vercel --prod

# Or push to GitHub and import into Vercel / GitHub Pages
```

## Before-and-After Verification Protocol
1. **Baseline Audit (Before):**
   - Query ChatGPT, Perplexity, and Gemini: *"What is IncuBrix and what features does it offer?"*
   - Note baseline lack of deep feature citation or missing structured specs.
2. **Indexing (After):**
   - Submit `https://<deployed-url>/sitemap.xml` to Google Search Console.
   - Ping Perplexity and Gemini via citation queries referencing the deployed domain.
3. **Measurement:**
   - Run `python -m src.cli run --day 2` in the visibility engine to log the citation share delta in `data/visibility.db` and Tab `02_QUESTIONS`.
