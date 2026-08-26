# Sources

Cited 2026 public medians. Not Dakota's books. Not a claimed survey.

## Rate medians (`trade-rates.csv`)

WhatShouldICharge — https://whatshouldicharge.io/statistics/freelance-rates-2026
BLS-derived medians across 21 professions; free to republish with a link. Page dated 2026-06-09. National median cited on that page: **$105/hr**.

| trade | rate_usd | page row |
| --- | ---: | --- |
| voice_over | 200 | Voice-Over Artists |
| brand_strategy | 175 | Brand Strategists |
| marketing_consult | 150 | Marketing Consultants |
| photography | 150 | Photographers |
| dev_app | 140 | Software Developers |
| seo | 125 | SEO Consultants |
| pr | 125 | PR Specialists |
| ui_ux | 120 | UI/UX Designers |
| ppc | 120 | PPC Specialists |
| motion | 110 | Motion Designers |
| web_design | 105 | Web Developers |
| webflow | 100 | Webflow Developers |
| meta_ads | 100 | Meta Ads Specialists |
| presentation | 100 | Presentation Designers |
| illustration | 100 | Illustrators |
| copywriting | 85 | Copywriters |
| video_edit | 85 | Video Editors |
| social_mgmt | 85 | Social Media Managers |
| graphic_design | 75 | Graphic Designers |
| podcast_edit | 75 | Podcast Editors |
| virtual_assistant | 45 | Virtual Assistants |

TryPros — https://trypros.com/freelance-market-rates-2026/
Aggregated Upwork / Fiverr / Toptal / Hubstaff / Jobbers / Payoneer / PayScale through **March 2026**. Medians are 25th–75th US bands' midpoint as published on that page.

| trade | rate_usd | page row |
| --- | ---: | --- |
| business_consult | 175 | Business Consulting |
| cloud | 140 | Cloud Architecture |
| devops | 125 | DevOps Engineering |
| ghostwriting | 110 | Ghostwriting |
| mobile | 110 | Mobile Development |
| growth | 110 | Growth Marketing |
| fullstack | 100 | Full-Stack Development |
| grant_writing | 90 | Grant Writing |
| web_react | 90 | Web Development (React, Next.js) |
| project_mgmt | 85 | Project Management |
| ux_writing | 85 | UX Writing / Microcopy |
| tech_writing | 80 | Technical Writing |
| shopify | 75 | Shopify/E-commerce Development |
| dev_wordpress | 65 | WordPress Development |
| email_marketing | 60 | Email Marketing |
| qa | 55 | QA/Testing |
| blog_writing | 50 | Blog/Article Writing |
| bookkeeping | 45 | Bookkeeping |
| va_general | 35 | Virtual Assistant (General) |

Where both pages list a similar skill, this desk **keeps the WhatShouldICharge BLS-derived median** (e.g. `ui_ux` $120, `social_mgmt` $85) and does not average the two.

## Metro multipliers (`metro-rpp.csv`)

Same WhatShouldICharge page, stats 30–34, BEA Regional Price Parity:

`local_rate_usd = round(national_median_usd * rpp)`

San Francisco 1.18, New York 1.15, Denver 1.03, Chicago 1.01, Austin 0.97.

## Platform fees (`platform-fees.csv`)

Same page, stats 41–44: Fiverr 20% flat; Upwork ~10% average (0–15% variable). Example $60,000 gross → $12,000 Fiverr commission is the page's own illustration.

## Salary floor (`salary-floor.csv`)

Same page: ~1,200 billable hours/year; 30–40% of the week unbillable; self-employment tax 15.3%; $100k employee ≈ $130k–$150k freelance gross (1.3x–1.5x). Rows other than $100k apply that published multiple — they are **modeled**, labeled as such.

## What is *not* a measurement

- Hours inside generated quote sheets — priors. Overwrite with your books.
- `module-catalog.csv` prices — Night Shift Foundry list prices for this desk, not market survey data.

If a public median moves, replace the CSV cell and keep the URL. Do not advertise these files as client data.
