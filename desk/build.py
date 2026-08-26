#!/usr/bin/env python3
"""Turn a buyer brief into a quote and the exact pack they pay for.

No network. No Gamut. No API keys.

  python3 desk/build.py quote briefs/example-wedding-photo.json
  python3 desk/build.py build briefs/example-wedding-photo.json --out /tmp/pack
  python3 desk/build.py catalog
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "data" / "module-catalog.csv"
RATES = ROOT / "data" / "trade-rates.csv"
SCHEMA_REQUIRED = {"buyer_handle", "product_name", "audience", "niche", "modules"}
TONES = {"plain", "firm", "warm"}
FLOOR_USD = 29
CAP_USD = 49
RESALE_ADD = 0  # license is included; price is module-sum clamped to band

WARM = {
    "hi": "Hi",
    "close": "Thanks for trusting me with this —",
    "pause": "I want to protect the date we already promised, so I'm pausing extras until we confirm.",
}
PLAIN = {
    "hi": "Hi",
    "close": "—",
    "pause": "Pausing anything beyond the original scope until you confirm.",
}
FIRM = {
    "hi": "Hello",
    "close": "—",
    "pause": "I will not start extra work until this is approved in writing.",
}


def slug(s: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return s[:60] or "pack"


def load_catalog() -> list[dict]:
    with CATALOG.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_rates() -> dict[str, dict]:
    with RATES.open(encoding="utf-8") as f:
        return {r["trade"]: r for r in csv.DictReader(f)}


def by_name(catalog: list[dict]) -> dict[str, dict]:
    return {r["name"]: r for r in catalog}


def brief_hash(brief: dict) -> str:
    canon = json.dumps(brief, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canon.encode()).hexdigest()[:12]


def validate(brief: dict, catalog: list[dict], rates: dict) -> list[str]:
    errors = []
    missing = SCHEMA_REQUIRED - set(brief)
    if missing:
        errors.append(f"missing fields: {sorted(missing)}")
    names = by_name(catalog)
    mods = brief.get("modules") or []
    if not isinstance(mods, list) or len(mods) < 2 or len(mods) > 8:
        errors.append("modules must be 2–8 names from the catalog")
    else:
        unknown = [m for m in mods if m not in names]
        if unknown:
            errors.append(f"unknown modules: {unknown}")
    trades = brief.get("trades") or []
    if trades:
        bad = [t for t in trades if t not in rates]
        if bad:
            errors.append(f"unknown trades: {bad}. catalog: {sorted(rates)}")
    tone = brief.get("tone", "plain")
    if tone not in TONES:
        errors.append(f"tone must be one of {sorted(TONES)}")
    return errors


def quote(brief: dict, catalog: list[dict]) -> dict:
    names = by_name(catalog)
    mods = []
    raw = 0
    for name in brief["modules"]:
        row = names[name]
        usd = int(row["base_usd"])
        raw += usd
        mods.append({"name": name, "usd": usd, "kind": row["kind"], "adds": row["adds"]})
    if brief.get("include_worked_example", True) and "worked_example" not in brief["modules"]:
        row = names["worked_example"]
        usd = int(row["base_usd"])
        raw += usd
        mods.append({"name": "worked_example", "usd": usd, "kind": row["kind"], "adds": row["adds"]})
    priced = min(CAP_USD, max(FLOOR_USD, raw))
    h = brief_hash(
        {
            "product_name": brief["product_name"],
            "audience": brief["audience"],
            "niche": brief["niche"],
            "trades": brief.get("trades") or [],
            "modules": [m["name"] for m in mods],
            "tone": brief.get("tone", "plain"),
        }
    )
    return {
        "sku": f"BRIEF-{h.upper()}",
        "brief_hash": h,
        "product_name": brief["product_name"],
        "raw_usd": raw,
        "price_usd": priced,
        "band": f"${FLOOR_USD}–${CAP_USD}",
        "modules": mods,
        "trades": brief.get("trades") or [],
        "tone": brief.get("tone", "plain"),
        "files_you_get": files_for(mods, brief),
    }


def files_for(mods: list[dict], brief: dict) -> list[str]:
    files = ["README.md", "LICENSE", "SPEC.md", "QUOTE.json"]
    for m in mods:
        n = m["name"]
        if n == "intake_form":
            files.append("templates/intake.md")
        elif n == "scope_recap":
            files.append("templates/recap.md")
        elif n == "change_order":
            files.append("templates/change-order.md")
        elif n == "email_ladder":
            files.append("templates/emails-change.md")
        elif n == "onboarding_sop":
            files.append("sop/onboarding.md")
        elif n == "cited_rate_card":
            files.append("data/rate-card.csv")
        elif n == "quote_sheet":
            files.append("data/quote-sheet.csv")
        elif n == "loss_bench":
            files.append("data/loss-bench.csv")
        elif n == "preflight_qa":
            files.append("checklists/preflight.md")
        elif n == "offer_page":
            files.append("copy/offer-page.md")
        elif n == "delivery_sop":
            files.append("sop/delivery.md")
        elif n == "revision_sop":
            files.append("sop/revisions.md")
        elif n == "welcome_3":
            files.append("templates/emails-welcome.md")
        elif n == "dunning_4":
            files.append("templates/emails-dunning.md")
        elif n == "worked_example":
            files.append("examples/worked-example.md")
    return sorted(set(files))


def voice(brief: dict) -> dict:
    return {"warm": WARM, "firm": FIRM}.get(brief.get("tone", "plain"), PLAIN)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + "\n", encoding="utf-8")


def render_pack(brief: dict, q: dict, rates: dict, out: Path) -> None:
    v = voice(brief)
    niche = brief["niche"]
    name = brief["product_name"]
    aud = brief["audience"]
    trades = q["trades"] or ["web_design"]
    selected = [rates[t] for t in trades if t in rates]
    chosen = {m["name"] for m in q["modules"]}

    write(
        out / "SPEC.md",
        f"""# Spec — {name}

This folder is the product you paid for. It was generated from your brief.
If a file is listed in `QUOTE.json` → `files_you_get`, it is in scope. Nothing else is.

- SKU: `{q['sku']}`
- brief_hash: `{q['brief_hash']}`
- price: ${q['price_usd']} USD (raw module sum ${q['raw_usd']}, clamped to {q['band']})
- niche: {niche}
- audience: {aud}
- tone: {q['tone']}
- trades: {', '.join(trades)}
- modules: {', '.join(m['name'] for m in q['modules'])}

Do not start extra modules without a new brief + new quote.
""",
    )
    write(out / "QUOTE.json", json.dumps(q, indent=2))
    write(
        out / "README.md",
        f"""# {name}

{aud}. Built for **{niche}**.

## What you paid for

This pack is generated from your brief (`brief_hash` `{q['brief_hash']}`). Price **${q['price_usd']} USD**.

## Files

{chr(10).join('- `' + f + '`' for f in q['files_you_get'])}

## Quick start

1. Open `SPEC.md` — that is the contract of files.
2. Fill every `[bracket]` with your client’s names.
3. Overwrite hours in any CSV with your own books. Rates are cited 2026 medians, not your rate.

No app. No login. Works if Night Shift Foundry is offline.
""",
    )
    write(
        out / "LICENSE",
        f"""Night Shift Foundry — commissioned pack license

SKU: {q['sku']}
brief_hash: {q['brief_hash']}

This generated pack is licensed to the paying buyer for use on their own client work
and for resale of *this generated folder* as their product, if they keep data/SOURCES
notes (when present) so cited rates stay attributed.

The generator (`custom-brief-desk`) itself is a separate SKU. Paying for one generated
pack does not transfer the generator.

THE FILES ARE PROVIDED AS-IS, WITHOUT WARRANTY.
""",
    )

    if "intake_form" in chosen:
        write(
            out / "templates/intake.md",
            f"""# Intake — {niche}

For: {aud}

## Job

- Working title:
- Event / launch / due date:
- What “done” looks like in one sentence:

## Must include

1.
2.
3.

## Must not include (out of scope unless a change order)

1.
2.

## Decision makers

- Approver (one name):
- Who else will comment (and when):

## Money

- Budget band:
- Rate we already quoted (if any):

Return this before work starts. Unsigned extras are not in the job.
""",
        )

    if "scope_recap" in chosen:
        write(
            out / "templates/recap.md",
            f"""# Recap — {niche}

**Date:**
**Client:**
**Original job:**

## Already agreed

-

## Just requested

-

## Impact

- Extra hours (yours):
- Extra fee:
- Date shift:

Reply **approved**, **hold**, or **swap [item]** by [time].
If I do not hear back I keep the original job only.

{v['close']} [your name]
""",
        )

    if "change_order" in chosen:
        write(
            out / "templates/change-order.md",
            f"""# Change order — {niche}

**CO #:** [YYYYMMDD-01]
**Job:** {name}

| Field | Detail |
| --- | --- |
| Request | |
| Extra hours | |
| Extra fee (USD) | |
| New date | |
| What slips | |

Work in this order does **not** start until the client replies **approved**.

Prior fee $ + this CO $ = new total $
""",
        )

    if "email_ladder" in chosen:
        write(
            out / "templates/emails-change.md",
            f"""# Emails — {niche} extras

## Soft

{v['hi']} [name] —

Quick recap from [call]. Original job: [one line]. New request: [their words].
I can fold a small version in, or price it as a change.

Reply “looks right” today.

{v['close']} [you]

## Priced

{v['hi']} [name] —

You asked for [request], which sits outside [original]. Extra hours [n], fee $[fee], new date [date].
Reply **approved** and I start. Silence keeps the original job.

{v['close']} [you]

## Pause

{v['hi']} [name] —

{v['pause']}

Requested: [one line]. Take it: $[fee], date [date]. Hold it: original date and fee.

{v['close']} [you]
""",
        )

    if "onboarding_sop" in chosen:
        write(
            out / "sop/onboarding.md",
            f"""# Onboarding SOP — {niche}

Day 0: send intake. Do not schedule production until it is back.
Day 1: confirm approver + due date in one email.
Day 2: lock the “must not include” list. Anything later is a change order.
Day 3: start production on the locked list only.
""",
        )

    if "delivery_sop" in chosen:
        write(
            out / "sop/delivery.md",
            f"""# Delivery SOP — {niche}

1. Export finals with the names in the brief.
2. Send a 5-line note: what is in the folder, what is not, when revisions expire.
3. Invoice the same day.
4. Extras after this email need a change order, not a “quick tweak.”
""",
        )

    if "revision_sop" in chosen:
        write(
            out / "sop/revisions.md",
            f"""# Revisions vs changes — {niche}

A **revision** is a fix to something already in the agreed list (wrong crop, typo, color that was specified).

A **change** is a new thing (another page, another person, another hour on site).

Revisions included: [n]. After that, every change uses the change-order template.
""",
        )

    if "welcome_3" in chosen:
        write(
            out / "templates/emails-welcome.md",
            f"""# Welcome sequence — {niche} digital sale

1. Receipt + download + what “done” looks like.
2. Day 2: one worked tip using this pack (point at examples/).
3. Day 5: ask which module they used; do not pitch extras in this email.
""",
        )

    if "dunning_4" in chosen:
        write(
            out / "templates/emails-dunning.md",
            f"""# Invoice ladder — {niche}

1. Due day: invoice attached, due date in the subject.
2. +7: “checking this arrived.”
3. +14: restated amount + late fee if your contract has one.
4. +21: pause remaining work until paid.
""",
        )

    if "preflight_qa" in chosen:
        write(
            out / "checklists/preflight.md",
            f"""# Preflight — {name}

- [ ] Filename matches the listing
- [ ] SPEC.md file list matches the folder
- [ ] Every `[bracket]` is either filled or obviously a placeholder
- [ ] License says who may resell
- [ ] No secrets, no client names from a real job
- [ ] Price on the listing matches QUOTE.json
""",
        )

    if "offer_page" in chosen:
        box = "\n".join(f"- {m['name']} (${m['usd']})" for m in q["modules"])
        write(
            out / "copy/offer-page.md",
            f"""# {name}

**For:** {aud}
**Does:** turns a messy {niche} job into the files listed in SPEC.md.
**Price:** ${q['price_usd']}
**Not:** a live agency, a Notion OS, or a custom app.

## What's in the box

{box}
""",
        )

    if "cited_rate_card" in chosen:
        lines = ["trade,rate_usd,source"]
        for r in selected:
            lines.append(f"{r['trade']},{r['rate_usd']},{r['source']}")
        write(out / "data/rate-card.csv", "\n".join(lines))
        write(out / "data/SOURCES.md", (ROOT / "data" / "SOURCES.md").read_text(encoding="utf-8"))

    if "quote_sheet" in chosen:
        lines = ["item,hours_mid,rate_usd,fee_mid_usd,notes"]
        for r in selected:
            rate = int(r["rate_usd"])
            for item, hours in (("core_delivery", 8), ("extra_revision_round", 4), ("rush_48h", 6)):
                lines.append(f"{r['trade']}:{item},{hours},{rate},{hours * rate},overwrite hours")
        write(out / "data/quote-sheet.csv", "\n".join(lines))

    if "loss_bench" in chosen:
        lines = ["trade,assumed_unpaid_hours,rate_usd,modeled_leak_usd,formula"]
        for r in selected:
            rate = int(r["rate_usd"])
            hours = 6.0
            leak = int(round(hours * rate))
            lines.append(f"{r['trade']},{hours},{rate},{leak},leak = unpaid_hours * rate (prior hours, cited rate)")
        write(out / "data/loss-bench.csv", "\n".join(lines))

    if "worked_example" in chosen:
        write(
            out / "examples/worked-example.md",
            f"""# Worked example — {niche}

A {aud.split()[0].lower() if aud else 'buyer'} sold a fixed {niche} job. Mid-way the client asked for one extra deliverable that was not on the intake.

They sent `templates/recap.md` the same day, attached `templates/change-order.md` if those files are in this pack, and did not start the extra until **approved**.

Numbers: use `data/quote-sheet.csv` if present; otherwise write your hours × your rate. This story is a shape, not a claimed sale.
""",
        )


def cmd_catalog() -> None:
    print("modules (pick 2–8):")
    for r in load_catalog():
        print(f"  {r['name']:<22} ${int(r['base_usd']):>2}  {r['kind']:<10} {r['description']}")
    print("\ntrades:")
    for t, r in load_rates().items():
        print(f"  {t:<18} ${r['rate_usd']}/h  {r['source']}")


def cmd_quote(path: Path) -> dict:
    brief = json.loads(path.read_text(encoding="utf-8"))
    catalog, rates = load_catalog(), load_rates()
    errs = validate(brief, catalog, rates)
    if errs:
        print("invalid brief:", file=sys.stderr)
        for e in errs:
            print(" -", e, file=sys.stderr)
        sys.exit(2)
    q = quote(brief, catalog)
    print(json.dumps(q, indent=2))
    return q


def cmd_build(path: Path, out: Path) -> None:
    brief = json.loads(path.read_text(encoding="utf-8"))
    catalog, rates = load_catalog(), load_rates()
    errs = validate(brief, catalog, rates)
    if errs:
        print("invalid brief:", file=sys.stderr)
        for e in errs:
            print(" -", e, file=sys.stderr)
        sys.exit(2)
    q = quote(brief, catalog)
    dest = out or Path("build") / slug(brief["product_name"])
    if dest.exists():
        for p in dest.rglob("*"):
            if p.is_file():
                p.unlink()
    render_pack(brief, q, rates, dest)
    (dest / "brief.json").write_text(json.dumps(brief, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {dest}  sku={q['sku']}  ${q['price_usd']}  files={len(q['files_you_get'])}")


def main() -> None:
    p = argparse.ArgumentParser(description="Custom brief desk")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("catalog")
    q = sub.add_parser("quote")
    q.add_argument("brief")
    b = sub.add_parser("build")
    b.add_argument("brief")
    b.add_argument("--out", default="")
    args = p.parse_args()
    if args.cmd == "catalog":
        cmd_catalog()
    elif args.cmd == "quote":
        cmd_quote(Path(args.brief))
    else:
        cmd_build(Path(args.brief), Path(args.out) if args.out else None)


if __name__ == "__main__":
    main()
