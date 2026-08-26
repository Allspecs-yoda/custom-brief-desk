# Custom Brief Desk

Interactive foundry counter: you specify the pack, the desk quotes it, and it writes **exactly those files**.

This is Night Shift **Foundry**, not a forge. No private repos. No agent required after download.

## Who it's for

A stranger who found a foundry listing and wants a desk for *their* niche — wedding photo extras, SaaS copy onboarding, etc. — not a generic Notion OS.

## Multi-buyer + exact spec

- Unlimited people may buy this **generator**.
- Each generated pack is what *that* brief paid for (`brief_hash` in `SPEC.md` / `QUOTE.json`).
- File a `BRIEF:` issue on [foundry-ledger](https://github.com/Allspecs-yoda/foundry-ledger) or run locally.

## What's included

- `data/module-catalog.csv` — 15 priced modules
- `data/trade-rates.csv` — **40** cited 2026 medians (WhatShouldICharge BLS-derived + TryPros March 2026)
- `data/metro-rpp.csv` — 5 BEA RPP metros; `local_rate = round(median * rpp)`
- `data/platform-fees.csv` — Fiverr 20% / Upwork ~10% from the same 2026 page
- `data/salary-floor.csv` — 1.3x–1.5x salary → freelance gross ÷ 1,200 hours
- `desk/rate-lookup.py` — offline lookup (trade / metro / platform / salary)
- `desk/build.py` — `catalog` / `quote` / `build`
- `briefs/schema.json` + two example briefs

## Quick start

```bash
python3 desk/build.py catalog
python3 desk/rate-lookup.py --trade photography --metro san_francisco
python3 desk/rate-lookup.py --platform fiverr --gross 60000
python3 desk/build.py quote briefs/example-wedding-photo.json
python3 desk/build.py build briefs/example-wedding-photo.json --out ./pack
```

Open `pack/SPEC.md`. If a file is not on that list, it is not what you paid for.

## After Gamut credits expire

On any laptop, with `foundry-ledger`:

```bash
python3 ../foundry-ledger/alchemy.py --write briefs/next.json
python3 desk/build.py build briefs/next.json --out ../next-pack
```

Hourly cron can do the same. The foundry keeps shipping.

## Price

**$49 USD** for the generator (unlimited buyers). A generated pack quotes **$29–$49** from the module sum (clamped).

Pay: https://buy.stripe.com/28EaEYaJW9352lk7s1cIE02

Then open a GitHub issue titled `CLAIM: Custom Brief Desk` with the receipt last-4. If checkout is down, star + watch [foundry-ledger](https://github.com/Allspecs-yoda/foundry-ledger) and open the same CLAIM issue.

This listing does not claim any sales.

## License

Commercial resale of **generated packs** you paid to build. The generator repo stays Dakota’s listing. See `LICENSE`.

## Foundry

Shipped by Night Shift Foundry for Dakota (@Allspecs-yoda).
SKU: `NSF-20260826-CUSTOM-BRIEF` | Decision: list | Cycle: 2026-08-26 | Ticket: $49
