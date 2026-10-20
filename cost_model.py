#!/usr/bin/env python3
"""Agent computer cost model.

Prices an agent workload from published compute rates. It makes no network
calls and needs no credentials: rates come from a JSON file you keep in the
repo, defaults below match Kortix's published rates.

    python3 cost_model.py workload.example.json
    python3 cost_model.py workload.example.json --rates rates.json

The model is deliberately plain arithmetic, so a finance reviewer can read
the whole calculation in one screen and change any assumption in the
workload profile instead of arguing about the total.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

# Published rates, per unit. Update from the vendor's own pricing page and
# keep the source URL with the number: a rate without a date and a URL is a
# rumour by the time a budget review reads it.
DEFAULT_RATES = {
    "source": "https://kortix.com/pricing",
    "checked": "2026-10-20",
    "vcpu_hour_usd": 0.0324,
    "memory_gb_hour_usd": 0.0108,
    "storage_gb_month_usd": 0.0526,
    "credit_usd": 0.01,
    "credits_per_agent_hour": 11,
}


@dataclass
class Agent:
    name: str
    runs_per_working_day: float
    minutes_per_run: float
    vcpu: float = 2
    memory_gb: float = 4
    storage_gb: float = 20


@dataclass
class Workload:
    working_days_per_month: float = 21
    agents: list[Agent] = field(default_factory=list)


def monthly_compute(workload: Workload, rates: dict) -> dict:
    rows = []
    total_vcpu = total_mem = total_storage = 0.0
    for agent in workload.agents:
        hours = agent.runs_per_working_day * workload.working_days_per_month
        hours *= agent.minutes_per_run / 60.0
        vcpu_cost = hours * agent.vcpu * rates["vcpu_hour_usd"]
        mem_cost = hours * agent.memory_gb * rates["memory_gb_hour_usd"]
        # Storage is billed for the month whether the computer runs or not.
        storage_cost = agent.storage_gb * rates["storage_gb_month_usd"]
        rows.append(
            {
                "agent": agent.name,
                "computer_hours": round(hours, 2),
                "vcpu_usd": round(vcpu_cost, 2),
                "memory_usd": round(mem_cost, 2),
                "storage_usd": round(storage_cost, 2),
                "subtotal_usd": round(vcpu_cost + mem_cost + storage_cost, 2),
                "credits": round(hours * rates["credits_per_agent_hour"], 0),
            }
        )
        total_vcpu += vcpu_cost
        total_mem += mem_cost
        total_storage += storage_cost
    return {
        "rows": rows,
        "total_usd": round(total_vcpu + total_mem + total_storage, 2),
        "total_computer_hours": round(sum(r["computer_hours"] for r in rows), 2),
        "total_credits": round(sum(r["credits"] for r in rows), 0),
        "parts": {
            "vcpu_usd": round(total_vcpu, 2),
            "memory_usd": round(total_mem, 2),
            "storage_usd": round(total_storage, 2),
        },
    }


def load_workload(path: Path) -> Workload:
    raw = json.loads(path.read_text())
    agents = [Agent(**item) for item in raw.get("agents", [])]
    if not agents:
        raise SystemExit(f"{path}: no agents in the workload profile")
    return Workload(
        working_days_per_month=raw.get("working_days_per_month", 21),
        agents=agents,
    )


def render(result: dict, rates: dict) -> str:
    head = f"{'agent':<18}{'hours':>8}{'vCPU':>9}{'memory':>9}{'storage':>9}{'total':>9}"
    lines = [
        f"rates from {rates['source']} (checked {rates['checked']})",
        head,
        "-" * len(head),
    ]
    for row in result["rows"]:
        lines.append(
            f"{row['agent']:<18}{row['computer_hours']:>8}{row['vcpu_usd']:>9}"
            f"{row['memory_usd']:>9}{row['storage_usd']:>9}{row['subtotal_usd']:>9}"
        )
    parts = result["parts"]
    lines += [
        "-" * len(head),
        f"vcpu {parts['vcpu_usd']} + memory {parts['memory_usd']} "
        f"+ storage {parts['storage_usd']} = {result['total_usd']} per month",
        f"{result['total_computer_hours']} agent-computer hours, "
        f"{int(result['total_credits'])} credits",
        "model calls are not included; they are billed by the model provider",
    ]
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workload", type=Path)
    parser.add_argument("--rates", type=Path, default=None)
    parser.add_argument("--json", action="store_true", help="print the result as JSON")
    args = parser.parse_args(argv)

    rates = DEFAULT_RATES
    if args.rates:
        rates = {**DEFAULT_RATES, **json.loads(args.rates.read_text())}

    result = monthly_compute(load_workload(args.workload), rates)
    print(json.dumps(result, indent=2) if args.json else render(result, rates))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
