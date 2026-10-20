# Fitting an open source cost model to your own rates

Kortix is the open-source AI Operating System. The program in this repository ships with its published rates as defaults. This open source model exists so you can swap those for your provider's numbers, or for the server you already own, and price the same schedule both ways. Five keys carry every rate. A rates file may set any subset of them.

## The five rate keys

| Key | Unit | Default |
| --- | --- | --- |
| vcpu_hour_usd | dollars per vCPU-hour | 0.0324 |
| memory_gb_hour_usd | dollars per GB-hour of RAM | 0.0108 |
| storage_gb_month_usd | dollars per GB-month of disk | 0.0526 |
| credit_usd | dollars per credit | 0.01 |
| credits_per_agent_hour | credits per running hour | 11 |

Two more fields, `source` and `checked`, are printed above the table. They do not affect the arithmetic. Fill them with the URL you read and the date you read it. A rates file that changes one number is one line:

```json
{"vcpu_hour_usd": 0.0308}
```

```bash
python3 cost_model.py workload.example.json --rates rates.json
```

The rest of the defaults stay in place. That matters when a provider publishes cores and memory but bundles disk into the price of the server. It is the usual shape for a machine you reserve.

## Pricing a server you reserve

A reserved instance is sold as a monthly figure. The work is to turn it into a rate per unit the model understands. Take a box at $180 a month with 8 vCPU and 32 GB, over a month of 730 hours:

```
180 / 730          = 0.2466   dollars per hour, whole box
0.2466 / 8         = 0.0308   dollars per vCPU-hour
0.2466 / 32        = 0.0077   dollars per GB-hour
```

Run the four-agent example against those two rates with storage set to 0, since the disk belongs to the reservation:

```json
{"vcpu_hour_usd": 0.0308, "memory_gb_hour_usd": 0.0077, "storage_gb_month_usd": 0}
```

The model reports $7.83 for the month: $5.22 of cores and $2.61 of memory. The bill from the provider is $180. Both numbers are correct about different things. The gap is the whole argument.

The reservation is charged for all 730 hours. The schedule uses 84.7 of them, about 12% of the machine. The per-hour rate therefore only reaches your invoice if enough agents keep the box busy. Price the month, not the hour, until the schedule can fill it. Splitting one box across agents means they share the cores, and the model has no notion of contention. Four agents each asking for 2 vCPU on an 8 vCPU box is a plan, not a guarantee, once two of them run together.

A metered provider can be cheaper than a reservation for one reason: it does not charge for the hours nothing runs. That is what the "Nothing while it is stopped" line on [kortix.com/pricing](https://kortix.com/pricing) buys. A reserved instance cannot offer it.

## Do not leave out the person

Every figure above is missing the work of running the machine. Patching, capacity, the queue when it fills, and the hours someone spends answering why an agent failed at 09:00. Four hours a month of an engineer's time at $60 an hour is $240, which is more than the reservation itself.

Put it in. A self-hosted rate that leaves it out compares a machine you administer against a metered one somebody else operates. With both, the four-agent month on the reserved box is $180 plus $240, or $420 across 609 runs. That is $0.69 per run. The metered example is $13.36 across the same 609 runs, $0.022 each. The second figure is thirty times smaller. The person-hours explain the gap.

A short honest rates file for a self-hosted box has two shapes. If the box is shared with other work, use the per-hour split and say in the source field which share you assumed. If the box exists for agents alone, skip the per-run arithmetic and compare the monthly total directly. No per-hour rate recovers a fixed charge.

## Keeping the rates current

Rates move. Leave the URL and date in the rates file. Re-read the provider's page before a budget review instead of trusting a number from the last one. On the Kortix defaults that page is the only source of truth for the five keys above. One credit is $0.01. Eleven credits buy an hour of a 2 vCPU / 4 GB / 20 GB computer. Cores are $0.0324 per vCPU-hour, memory $0.0108 per GB-hour, and disk $0.0526 per GB-month, all checked 2026-10-20.

Run it on Kortix Cloud, in your VPC, or on your own on-prem network. Self-host is free. On a box you run yourself the reservation arithmetic still applies, so the compute rate is whatever your infrastructure costs. The rate file is where those two facts meet.
