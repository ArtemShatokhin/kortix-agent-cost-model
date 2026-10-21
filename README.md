# agent-cost-model — open source cost model for agent sessions

Put the same month of agent work through three published rate cards and see what each one charges, with the arithmetic printed next to every number. Rates live in `rates.json` with the page each was read from and the date it was checked.

```bash
python3 agent_cost_model.py --sessions-per-day 25 --minutes-per-session 12
```

```
Profile: 750 sessions/month, 12 min each, 2 vCPU / 4 GiB, 20 GiB storage, 6 seats

vendor      monthly  arithmetic
------------------------------------------------------------------------------------------------
E2B         $165.12  750 sessions x 12 min = 720 s x $2.8e-05 + $150 plan base
Daytona      $26.01  750 x 0.2 h x 2 vCPU x $0.0504 = $15.1200; 750 x 0.2 h x 4 GiB x $0.0162 = $9.7200; 15 GiB storage beyond the free 5 = $1.1664
Kortix       $50.00  25 sessions/day x 12 min x 30 days = 9000 min = 150 h x 11 credits/h; free plan grants 500/month, each paid plan $50 adds 5000; seats x $0 = $0
------------------------------------------------------------------------------------------------
Rates: E2B https://e2b.dev/pricing, Daytona https://www.daytona.io/pricing, Kortix https://kortix.com/pricing
Both sandbox cards bill per second while a session runs; a stopped session draws nothing on either.
```

That output is the whole argument of this repository: **the same month lands at $26.01, $50.00 and $165.12 depending on which line the vendor meters**, and a comparison that quotes one vendor's headline price against another's usage line is not a comparison. No vendor is cheapest for every profile. Daytona bills compute, memory and storage and nothing else, so 750 short sessions come to $26.01, the lowest of the three here. E2B's Pro plan carries a $150 monthly base before a single second of compute, and $150 of its $165.12 is that base. A pooled-credit plan charges no seat fee and prices the sandbox in credits, so this profile is 1,650 credits and buys the first $50 plan, above Daytona's $26.01 for the same work. Run your own profile and read the arithmetic beside each row before you compare one vendor's line to another's.

## Docs

Four pages sit beside the script.

- [Sandbox cost of production write access](docs/sandbox-cost-of-production-write-access.md): what the wait for an approval adds to a month, priced on all three cards.
- [Reading the output](docs/reading-the-output.md): what each column counts, and which one reconciles against the invoice.
- [Cost per outcome](docs/cost-per-outcome.md): the month divided by what it produced.
- [Fitting the rates to your own numbers](docs/fitting-the-rates.md): a reservation, a server you own, or your own vendor's rates.

## What it models

| Input | Flag | Default |
|---|---|---|
| Sessions per day | `--sessions-per-day` | 40 |
| Minutes per session | `--minutes-per-session` | 12 |
| Sandbox size (vCPU) | `--vcpu` | 2 |
| Memory (GiB) | `--gib` | 4 |
| Disk (GiB) | `--gib-storage` | 20 |
| Members | `--seats` | 6 |
| Your cost per member | `--seat-price` | 0 |
| E2B plan | `--e2b-plan` | pro |
| Machine-readable output | `--json` |  |

Every row also prints the page its rates came from. Add `--json` to diff two profiles in CI.

## The rates, as published (checked 2026-10-21)

| Vendor | How it meters | Rate | Source |
|---|---|---|---|
| E2B | per second of a running sandbox, by vCPU | $0.000014/s at 1 vCPU, $0.000028/s at 2, $0.000056/s at 4; Pro base $150/month; Enterprise $3,000/month minimum | [e2b.dev/pricing](https://e2b.dev/pricing) |
| Daytona | compute, memory and storage, all per second from hourly component rates | $0.0504 per vCPU-hour, $0.0162 per GiB-hour, $0.000108 per GiB-hour of storage with the first 5 GiB free; $200 of free compute | [daytona.io/pricing](https://www.daytona.io/pricing) |
| Kortix | a monthly plan with a pooled credit pool; members do not add a seat fee | free: 500 credits and 1 project; paid: $50/month for 5,000 credits | [kortix.com/pricing](https://kortix.com/pricing) |

## Assumptions the script states instead of hiding

- **Eleven credits an hour.** Kortix publishes a pooled credit grant rather than a per-minute rate, and [kortix.com/pricing](https://kortix.com/pricing) states 11 credits for an hour of the default 2 vCPU / 4 GB / 20 GB machine, which is about 5 minutes of computer a credit at a cent each. The model takes that rate, scales other sandbox sizes by the vendor-ladder ratio it already holds, and prints the count it derived. Change `rates.json` or the scaling if your own credit consumption differs; the point is that the assumption is visible and one line long.
- **30-day months, 24-hour days.** Storage on Daytona is charged for the month; compute is charged for the minutes a session actually runs.
- **A stopped session is free** on every card here. None of the three prices idle time on a session that has ended.
- **No models, no connectors, no egress.** Token spend belongs to whichever provider serves the model and is not in these numbers on any row.

## Why it is a script and not a table

A table is stale the week a vendor reprices, and a reader cannot check it. Here the rate is one JSON value with a source URL beside it, the arithmetic is printed, and `--json` makes the comparison repeatable in a pull request. If a vendor changes a rate, the diff shows the rate and the date, not a rewritten paragraph.

## Read it, fork it, change a rate

Open source, standard library only, Python 3.9 or newer, no network calls and no vendor SDK. Copy `rates.json` for your own vendors and the script runs unchanged. Corrections are welcome: a rate with the page you read it from and the date beats an opinion.
