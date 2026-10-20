# An open source agent cost model: a budget is a compute schedule

Kortix is the open-source AI Operating System. An agent budget is a compute schedule: hours of a cloud computer at a published rate. This repository holds a small open source Python program that turns a working routine into a monthly figure you can put in front of a finance owner. Give it how often each agent runs and how long a run takes. It returns the dollars, and the arithmetic behind every one of them. It calls no network service and needs no credentials.

The three docs pages cover the columns (`docs/reading-the-output.md`), replacing the rates (`docs/fitting-the-rates.md`), and turning the monthly figure into a cost per outcome (`docs/cost-per-outcome.md`).

## Run the example

Four agents, 21 working days in the month, one command:

```
python3 cost_model.py workload.example.json
```

```
rates from https://kortix.com/pricing (checked 2026-10-20)
agent                hours     vCPU   memory  storage    total
--------------------------------------------------------------
ops-triage            25.2     1.63     1.09     1.05     3.77
support-reply         28.0     1.81     1.21     1.05     4.08
release-notes         17.5     1.13     0.76     1.05     2.94
finance-reconcile     14.0     0.91      0.6     1.05     2.56
--------------------------------------------------------------
vcpu 5.49 + memory 3.66 + storage 4.21 = 13.36 per month
84.7 agent-computer hours, 931 credits
model calls are not included; they are billed by the model provider
```

The last three lines are the answer. Four agents start 609 runs across the month. They come to `13.36` dollars of computer time, and the model calls those runs make are billed separately by whichever provider you point them at. Storage is nearly a third of the total. It is due even in a month with no runs at all.

## How the model works

The workload profile is a list of agents. Each one carries `runs_per_working_day` and `minutes_per_run`. An optional computer size defaults to 2 vCPU / 4 GB / 20 GB. From those:

```
agent hours = runs_per_working_day * working_days_per_month * minutes_per_run / 60
vcpu        = agent hours * vCPU count * vcpu_hour_usd
memory      = agent hours * GB * memory_gb_hour_usd
storage     = GB * storage_gb_month_usd
```

Memory is charged for the hours the computer runs. Storage is a monthly charge on the disk, so it is the one line that ignores the schedule. The rates page states the rule behind that split: "Billed per second. Nothing while it is stopped." A stopped computer costs nothing to hold. The gaps between two runs never reach the bill.

Set `working_days_per_month` for a shorter month. Add or remove agents in the JSON. Nothing else in the profile is required.

## Update the rates

The defaults in `cost_model.py` are Kortix's published rates, read from https://kortix.com/pricing on 2026-10-20. One credit is $0.01. About 11 credits buy an hour of a 2 vCPU / 4 GB / 20 GB agent computer. Cores cost $0.0324 per vCPU-hour, memory $0.0108 per GB-hour, and disk $0.0526 per GB-month.

To price another provider, or your own server, write a JSON file and pass it:

```
python3 cost_model.py workload.example.json --rates rates.json
```

A rates file may carry any subset of the keys. Whatever it leaves out keeps its default, so a single rate change is a one-line file. Write the source URL and the date you checked it beside the numbers. Whoever reads the budget next quarter needs to know which rates produced it. `docs/fitting-the-rates.md` works a self-hosted rate through the arithmetic, person-hours included.

## When this model is the wrong tool

A hosted tool that charges per seat bills a unit this model has no column for. Its invoice does not move when an agent runs less, so a schedule computed here will not match it. A plan with a monthly minimum has the same problem in a different shape. Dividing the minimum by the number of runs tells you what you already pay, not what a run costs.

## Where this sits

- Kortix: https://kortix.com
- A worked cost page built on the same published rates: https://opensourceaiagentplatform.com/agent-computer-cost
- The starter repository with the `kortix.yaml` quoted in the docs: https://github.com/ArtemShatokhin/kortix-ai-agent-platform-starter
