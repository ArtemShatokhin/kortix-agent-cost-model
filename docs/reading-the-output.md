# Reading the output of an open source cost model

Kortix is the open-source AI Operating System. This open source model prices one part of it: the computer an agent runs on. Its output is six columns over four agents, then three summary lines. Each column answers a different question. Reading them out of order is how a defensible budget turns into an argument in a meeting.

## The columns

| Column | What it counts | Charged by |
| --- | --- | --- |
| hours | agent-computer hours the schedule adds up to | the running second |
| vCPU | dollars for cores at $0.0324 per vCPU-hour | vCPU-hour |
| memory | dollars for RAM at $0.0108 per GB-hour | GB-hour |
| storage | dollars for disk at $0.0526 per GB-month | GB-month |
| total | the three dollar columns added, per agent | month |
| credits | running hours at the published 11 credits an hour | credit |

The three dollar rates are the ones [kortix.com/pricing](https://kortix.com/pricing) publishes, checked 2026-10-20. They are the defaults the program ships with. The hour column is the only input. Everything after it follows from the number of runs and their length.

## Why storage is charged in a month with no runs

Storage is priced per GB-month, and the model applies it once per agent regardless of the schedule. Twenty gigabytes at $0.0526 is $1.05, for each of the four agents. That is $4.21 of the $13.36 total. A month in which every agent stayed stopped would still owe it, because the disk is allocated for the month. Remove an agent from the profile and its disk charge goes with it. That is the only lever the schedule does not control.

Memory works the other way. It is priced per GB-hour of running time, so the 4 GB an agent holds is charged only for the 14 to 28 hours that agent runs. The disk is a standing allocation. Memory and cores are metered.

## Why the credit column is the one to check

A plan is bought in credits, and the pricing page states that 1 credit = $0.01. An invoice, a credit pool, and a budget review all speak in that unit. The credit column is the one that reconciles against the bill. The example comes to 931 credits, about $9.31 of running time.

Two rounding details are worth knowing. Credits are rounded per agent before they are summed, so the four agents give 931. Multiplying 84.7 hours by 11 gives 932. And 11 is itself the published rounded figure: at the per-resource rates the same hour costs $0.108, which is 10.8 credits. So the credit column and the dollar columns differ by about 2%. Use the dollar columns to compare providers. Use the credit column to reconcile a plan.

Storage sits outside the credit column in this model. At 5.26 credits per GB-month it is another 421 credits across the four agents. Added to 931, the month comes to about 1,352 credits, or $13.52 at a cent each. The program prints $13.36 because its dollar columns use the per-resource rates and stop rounding at the cent.

## Two mistakes in the profile

### Counting wall-clock hours

The profile asks for minutes of computer time per run. It does not ask for the time the run occupies in someone's day. `finance-reconcile` runs 40 minutes once a day and bills 14 hours for the month. Count the two hours the session stays open, while someone thinks, answers an approval and comes back after lunch, and you have entered 42 hours. The total is triple the real charge. Measure a run by what the computer does. The run's own transcript carries its duration.

### Charging memory for a stopped computer

Billing stops when the computer stops, and memory follows that rule. A team that budgets a full working day of memory for each agent multiplies the bill by ten. Four agents held 10 hours a day for 21 days is 3,360 GB-hours at $0.0108, or $36.29, against the $3.66 the schedule charges. Idle gaps are why a schedule priced per second comes out this low. Take them back out and the model answers for a product nobody is billed for.

## Sanity checks before you share the number

Run the example as shipped and compare: 84.7 hours, 931 credits, $13.36. If your own profile lands far from that, check the working days first, then the minutes per run, then the agent count. A figure ten times the example usually means a wall-clock error. One slightly above it usually means an agent left in the profile that no longer runs.
