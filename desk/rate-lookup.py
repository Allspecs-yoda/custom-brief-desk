#!/usr/bin/env python3
"""Offline cited-rate lookup. No network. No API keys.

  python3 desk/rate-lookup.py --trade photography
  python3 desk/rate-lookup.py --trade photography --metro san_francisco
  python3 desk/rate-lookup.py --platform fiverr --gross 60000
  python3 desk/rate-lookup.py --salary 100000
  python3 desk/rate-lookup.py --list
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RATES = ROOT / "data" / "trade-rates.csv"
METRO = ROOT / "data" / "metro-rpp.csv"
FEES = ROOT / "data" / "platform-fees.csv"
FLOOR = ROOT / "data" / "salary-floor.csv"


def rows(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def cmd_list() -> None:
    print("trades (national median USD/hr):")
    for r in rows(RATES):
        print(f"  {r['trade']:<20} ${int(r['rate_usd']):>3}  {r['source']}")
    print("\nmetros (BEA RPP):")
    for r in rows(METRO):
        print(f"  {r['metro']:<16} rpp={r['rpp']}  {r['source']}")


def cmd_trade(trade: str, metro: str | None) -> None:
    rates = {r["trade"]: r for r in rows(RATES)}
    if trade not in rates:
        print(f"unknown trade {trade!r}. catalog: {sorted(rates)}", file=sys.stderr)
        sys.exit(2)
    r = rates[trade]
    national = int(r["rate_usd"])
    print(f"trade={trade}")
    print(f"national_median_usd={national}")
    print(f"source={r['source']}")
    print(f"url={r['source_url']}")
    if not metro:
        return
    metros = {m["metro"]: m for m in rows(METRO)}
    if metro not in metros:
        print(f"unknown metro {metro!r}. catalog: {sorted(metros)}", file=sys.stderr)
        sys.exit(2)
    m = metros[metro]
    rpp = float(m["rpp"])
    local = int(round(national * rpp))
    print(f"metro={metro}")
    print(f"rpp={rpp}")
    print(f"local_rate_usd={local}")
    print(f"formula={m['formula']}")
    print(f"metro_source={m['source']}")


def cmd_platform(platform: str, gross: int) -> None:
    fees = {r["platform"]: r for r in rows(FEES)}
    if platform not in fees:
        print(f"unknown platform {platform!r}. catalog: {sorted(fees)}", file=sys.stderr)
        sys.exit(2)
    r = fees[platform]
    pct = float(r["fee_pct"])
    fee = int(round(gross * pct))
    print(f"platform={platform}")
    print(f"gross_usd={gross}")
    print(f"fee_pct={pct}")
    print(f"fee_usd={fee}")
    print(f"net_after_platform_usd={gross - fee}")
    print(f"formula=fee = gross * fee_pct")
    print(f"source={r['source']}")
    print(f"url={r['source_url']}")
    print("note=does not include self-employment tax or health insurance")


def cmd_salary(salary: int) -> None:
    table = rows(FLOOR)
    match = next((r for r in table if int(r["target_employee_salary_usd"]) == salary), None)
    if match:
        print(f"target_employee_salary_usd={match['target_employee_salary_usd']}")
        print(f"freelance_gross_mid_usd={match['freelance_gross_mid_usd']}")
        print(f"freelance_gross_high_usd={match['freelance_gross_high_usd']}")
        print(f"billable_hours_year={match['billable_hours_year']}")
        print(f"floor_rate_mid_usd={match['floor_rate_mid_usd']}")
        print(f"source={match['source']}")
        print(f"url={match['source_url']}")
        print(f"notes={match['notes']}")
        return
    # apply published 1.3x mid / 1.5x high and 1200 hours from the $100k row
    mid = int(round(salary * 1.3))
    high = int(round(salary * 1.5))
    hours = 1200
    floor = int(round(mid / hours))
    print(f"target_employee_salary_usd={salary}")
    print(f"freelance_gross_mid_usd={mid}")
    print(f"freelance_gross_high_usd={high}")
    print(f"billable_hours_year={hours}")
    print(f"floor_rate_mid_usd={floor}")
    print("formula=gross_mid = salary * 1.3; floor = round(gross_mid / 1200)")
    print("source=WhatShouldICharge 2026 1.3x–1.5x multiple applied to your salary")
    print("url=https://whatshouldicharge.io/statistics/freelance-rates-2026")
    print("notes=modeled from published multiple — not a separate survey row")


def main() -> None:
    p = argparse.ArgumentParser(description="Cited 2026 rate lookup (offline)")
    p.add_argument("--list", action="store_true")
    p.add_argument("--trade")
    p.add_argument("--metro")
    p.add_argument("--platform")
    p.add_argument("--gross", type=int, default=60000)
    p.add_argument("--salary", type=int)
    args = p.parse_args()
    if args.list:
        cmd_list()
    elif args.trade:
        cmd_trade(args.trade, args.metro)
    elif args.platform:
        cmd_platform(args.platform, args.gross)
    elif args.salary is not None:
        cmd_salary(args.salary)
    else:
        p.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
