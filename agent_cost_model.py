#!/usr/bin/env python3
"""agent_cost_model - monthly cost of running agent sessions, from published rate cards.

Three vendors meter agent work three different ways. This script puts the same
session profile through each of them so the numbers are comparable, and prints
the arithmetic it used, so a reader can check a line by hand.

Rates live in rates.json next to this file, each with the page it was read from
and the date it was checked. Nothing here calls a vendor API.

Usage:
    python3 agent_cost_model.py --sessions-per-day 40 --minutes-per-session 12
    python3 agent_cost_model.py --sessions-per-day 40 --minutes-per-session 12 \
        --vcpu 2 --gib 4 --seat-price 0 --seats 6 --json
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

RATES_PATH = Path(__file__).with_name("rates.json")
DAYS_PER_MONTH = 30


def load_rates() -> dict:
    with RATES_PATH.open(encoding="utf-8") as fh:
        return json.load(fh)


def e2b_monthly(rates: dict, minutes: float, vcpu: int, plan: str, sessions: int) -> dict:
    e2b = rates["e2b"]
    per_second = e2b["per_second_by_vcpu"][str(vcpu)]
    seconds = minutes * 60
    usage = seconds * per_second * sessions
    base = e2b["pro_base_monthly_usd"] if plan == "pro" else 0.0
    return {
        "vendor": "E2B",
        "per_second_usd": per_second,
        "plan_base_usd": base,
        "monthly_usd": round(usage + base, 2),
        "arithmetic": (
            f"{sessions} sessions x {minutes:g} min = {seconds:g} s x ${per_second} "
            f"+ ${base:g} plan base"
        ),
        "source": e2b["source"],
    }


def daytona_monthly(rates: dict, minutes: float, vcpu: int, gib: float, gib_storage: float, sessions: int) -> dict:
    d = rates["daytona"]
    hours = minutes / 60
    compute = hours * vcpu * d["vcpu_hour_usd"] * sessions
    memory = hours * gib * d["gib_memory_hour_usd"] * sessions
    storage_gib = max(0.0, gib_storage - d["storage_free_gib"])
    storage = storage_gib * d["gib_storage_hour_usd"] * DAYS_PER_MONTH * 24
    return {
        "vendor": "Daytona",
        "compute_usd": round(compute, 4),
        "memory_usd": round(memory, 4),
        "storage_usd": round(storage, 4),
        "monthly_usd": round(compute + memory + storage, 2),
        "arithmetic": (
            f"{sessions} x {hours:g} h x {vcpu} vCPU x ${d['vcpu_hour_usd']} = ${compute:.4f}; "
            f"{sessions} x {hours:g} h x {gib:g} GiB x ${d['gib_memory_hour_usd']} = ${memory:.4f}; "
            f"{storage_gib:g} GiB storage beyond the free {d['storage_free_gib']} = ${storage:.4f}"
        ),
        "source": d["source"],
    }


def credits_monthly(rates: dict, sessions_per_day: int, minutes: float, vcpu: int, seats: int, seat_price: float) -> dict:
    """Kortix prices sandbox compute with credits, and members do not add a seat fee.

    One credit is treated as one minute of the default 2 vCPU sandbox: that is the
    assumption this model makes explicit, because the pricing page states the plan
    grants a credit pool, not a per-minute rate. Compute it as sessions x minutes and
    compare the pooled grants; the point of the line is the shape, not a credited rate.
    """
    k = rates["kortix_credits"]
    monthly_minutes = sessions_per_day * minutes * DAYS_PER_MONTH
    # Sandboxes below the default 2 vCPU are cheaper per unit of wall time; scale the
    # minutes by the vendor's own 1/2/4/8 vCPU ladder rather than inventing a factor.
    ladder = rates["e2b"]["per_second_by_vcpu"]
    scale = ladder[str(vcpu)] / ladder["2"]
    credits_needed = monthly_minutes / 60 * k["credits_per_hour"] * scale
    free_covers = credits_needed <= k["free_monthly_credits"]
    paid_plans = 0
    remainder = max(0.0, credits_needed - k["free_monthly_credits"])
    while remainder > 0:
        paid_plans += 1
        remainder -= k["paid_monthly_credits"]
    seat_cost = seats * seat_price
    return {
        "vendor": "Kortix",
        "credits_needed": round(credits_needed),
        "free_plan_covers": free_covers,
        "paid_plans_needed": paid_plans,
        "monthly_usd": round(paid_plans * k["paid_monthly_usd"] + seat_cost, 2),
        "arithmetic": (
            f"{sessions_per_day} sessions/day x {minutes:g} min x {DAYS_PER_MONTH} days "
            f"= {monthly_minutes:g} min = {monthly_minutes / 60:g} h x {k['credits_per_hour']} credits/h; "
            f"free plan grants {k['free_monthly_credits']}/month, "
            f"each paid plan ${k['paid_monthly_usd']} adds {k['paid_monthly_credits']}; "
            f"seats x ${seat_price:g} = ${seat_cost:g}"
        ),
        "source": k["source"],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sessions-per-day", type=int, default=40)
    ap.add_argument("--minutes-per-session", type=float, default=12.0)
    ap.add_argument("--vcpu", type=int, default=2, choices=[1, 2, 4, 6, 8])
    ap.add_argument("--gib", type=float, default=4.0)
    ap.add_argument("--gib-storage", type=float, default=20.0)
    ap.add_argument("--seats", type=int, default=6)
    ap.add_argument("--seat-price", type=float, default=0.0, help="your own cost per member, if you charge one")
    ap.add_argument("--e2b-plan", choices=["hobby", "pro"], default="pro")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    rates = load_rates()
    sessions_month = args.sessions_per_day * DAYS_PER_MONTH
    rows = [
        e2b_monthly(rates, args.minutes_per_session, args.vcpu, args.e2b_plan, sessions_month),
        daytona_monthly(rates, args.minutes_per_session, args.vcpu, args.gib, args.gib_storage, sessions_month),
        credits_monthly(rates, args.sessions_per_day, args.minutes_per_session, args.vcpu, args.seats, args.seat_price),
    ]
    out = {
        "profile": {
            "sessions_per_day": args.sessions_per_day,
            "sessions_per_month": sessions_month,
            "minutes_per_session": args.minutes_per_session,
            "vcpu": args.vcpu,
            "gib": args.gib,
            "gib_storage": args.gib_storage,
            "seats": args.seats,
        },
        "rows": rows,
    }
    if args.json:
        print(json.dumps(out, indent=2))
        return 0

    print(f"Profile: {sessions_month} sessions/month, {args.minutes_per_session:g} min each, "
          f"{args.vcpu} vCPU / {args.gib:g} GiB, {args.gib_storage:g} GiB storage, {args.seats} seats\n")
    print(f"{'vendor':<9} {'monthly':>9}  arithmetic")
    print("-" * 96)
    for row in rows:
        print(f"{row['vendor']:<9} {'$' + format(row['monthly_usd'], ',.2f'):>9}  {row['arithmetic']}")
    print("-" * 96)
    print("Rates: " + ", ".join(f"{r['vendor']} {r['source']}" for r in rows))
    print("Both sandbox cards bill per second while a session runs; a stopped session draws nothing on either.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
