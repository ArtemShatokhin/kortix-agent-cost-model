# Pricing an open source agent sandbox when every write needs approval

Sandboxing an agent that can write to production costs $26 a month on Daytona, $50 on Kortix and $165 on E2B's Pro plan. That is a five-person team running 300 sessions a month (checked October 2026). In the profile priced here, four fifths of the wall clock is a diff waiting for someone to open it. Kortix is the open-source AI Operating System: your agents, their skills, your company memory, and every connector in one git repo you own, with the agents working on real cloud computers.

The rates are in [rates.json](../rates.json), each with its source and check date. All three cards price a running sandbox. None has a line for the time a sandbox spends waiting for a person. An agent bill splits into software, machines and tokens; a [three-line breakdown](https://opensourceaiagentplatform.com/ai-agent-platform-pricing) keeps the machine line where a budget can see it.

## Two clocks in one session

Execution is the part of a session the sandbox spends working: reading the repository, running the tests, preparing the change request. The wait starts when that work is ready for review. It ends when a person approves it. A gate creates the wait. In Kortix the gate sits on the action, approval holds the call while the agent's turn pauses and resumes, and approval gates are off until you set them. A schedule with no `ask` rule has no second clock.

The model takes one number for minutes per session, so the split is two runs of the same profile: 6 minutes of execution, then 30 with the wait added. Those 24 minutes are an assumption, and the first one to replace. A team that approves in the chat window measures less. A team whose reviewer is asleep measures six hours, and a per-second meter notices.

## The month for a five-person team

Ten sessions a working day, 300 in the model's 30-day month, on the default 2 vCPU / 4 GiB / 20 GiB sandbox. Each card's month, with the sandbox held open and then without the wait.

| Vendor | Execution only | Held open | The wait costs |
| --- | --- | --- | --- |
| E2B | $153.02 | $165.12 | $12.10 |
| Daytona | $6.13 | $26.01 | $19.88 |
| Kortix | $0.00 | $50.00 | $50.00 |

```
300 sessions x 30 min held open, 2 vCPU / 4 GiB / 20 GiB, 30-day month

E2B      300 x 1800 s x 0.000028              = 15.12 + 150.00 base = 165.12
Daytona  300 x 0.5 h x (2 x 0.0504
         + 4 x 0.0162)                        = 24.84 +   1.17 disk =  26.01
Kortix   150 h x 11 credits = 1650 credits, one $50 plan          =  50.00
```

E2B's $150 Pro plan carries 91% of that bill. Four fifths of the session length moves the total by $12, so the card looks nearly immune to the wait. The base is a fixed cost. Fixed costs stop dominating as volume rises.

Daytona has no base, and its disk line is charged whether anything runs or not: 15 billable GiB at $0.000108 an hour is $1.17, or 4.5% of the held-open total. The rest is the wait. It is billed per second through two components that move with the clock.

Kortix shows a different shape. The wait costs about 4.4 cents a session there, against 6.6 on Daytona and 4.0 on E2B. The month still pays $50 for it. Execution alone is 330 credits, which the free 500-credit grant covers, so that month costs nothing. Held open, the same schedule is 1,650 credits and buys the first paid tier. A $13.20 wait gets invoiced as a $50 boundary.

At this size Daytona is the cheapest card by far. None of the three charges per seat, so a five-person team pays for sessions alone. [What a free tier covers in month two](https://opensourceaiagentplatform.com/open-source-ai-agent-platform-free) and the [small-business version of this bill](https://opensourceaiagentplatform.com/open-source-ai-agent-platform-for-small-business) are where a per-seat control plane would change that.

## Why the wait lands on one card and not another

E2B charges by the second of a running sandbox, $0.000028 a second at 2 vCPU, on top of a $150 Pro base ([E2B pricing](https://e2b.dev/pricing), checked October 2026). Sessions run up to 24 hours; Enterprise carries a $3,000 monthly minimum. A session that stays alive while a reviewer reads is a running sandbox, so the wait is billed at the rate of the work. At $0.1008 an hour it is the cheapest of the three.

Daytona prices three components per second, from hourly rates of $0.0504 per vCPU-hour, $0.0162 per GiB-hour of memory and $0.000108 per GiB-hour of disk, with the first 5 GiB free ([Daytona pricing](https://www.daytona.io/pricing), checked October 2026). New accounts get $200 of free compute, which covers the $24.84 of session time in the first month. A held-open wait costs 0.4 hours of two components, about 6.6 cents. That makes Daytona the dearest per hour at $0.1656 and the cheapest at low volume.

Kortix prices the sandbox in credits, 11 to an hour at a cent each, so the default machine is about $0.11 an hour. It bills per second while it runs and, in the pricing page's words, "costs nothing while it is stopped" ([Kortix pricing](https://kortix.com/pricing), checked October 2026). Managed model calls draw on the same credits. Unused credits roll over one month, and members are unlimited and free on one shared pool. That pool is why the wait behaves like a step. It is bought in blocks of 5,000, and a session that crosses a block boundary costs a block.

## The same schedule at fifty people

A hundred sessions a working day is 3,000 a month, and the cheapest card changes. Held open, Kortix lands at $200, Daytona at $249.57 and E2B at $301.20. Without the wait, Kortix and Daytona sit within a dollar of each other, and E2B stays at $180.24.

E2B's base carries 91% of its bill at 300 sessions and 50% at 3,000, while usage grows tenfold. Daytona's hourly rate is the highest of the three, so every extra session adds most there. Kortix adds a plan step about every 454 sandbox hours. None of the three charges per seat, so team size moves the bill only through the sessions a larger team starts.

## Questions that decide the invoice

Five questions, each answerable from the vendor's own pricing page:

1. Does the meter run while a write waits for approval, and what stops it: the session ending, or an idle rule?
2. Is the unit a session, a concurrent sandbox, or a seat, and what happens when two sessions run at once?
3. What is the smallest increment billed? Kortix bills every five minutes and again on stop. The other two bill the second.
4. What happens when the month's grant runs out: does work stop, does a top-up trigger, or does the account go negative?
5. Is there a base or a minimum, and which parts of the month does it cover?

## What to measure before you sign

Approval latency is the input no rate card can supply, and the transcripts already hold it. Pull the timestamps between diff and approval on twenty write-access runs. Take the median and put it in place of the 24 minutes. The gap between the two columns, multiplied by the sessions a month, is what the gate costs on the card, and the number worth arguing about in a budget review.

Kortix prices the running sandbox and nothing while it is stopped, so a schedule whose sessions stop at the gate pays for execution alone. Run it on Kortix Cloud, in your VPC, or on your own on-prem network. Self-host is free. [Read the docs](https://kortix.com/docs/host) to stand one up.
