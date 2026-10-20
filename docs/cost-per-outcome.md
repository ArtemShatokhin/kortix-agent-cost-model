# Cost per outcome on an open source agent computer

Kortix is the open-source AI Operating System. This open source model prices the computer an agent runs on. A budget needs a different number: the cost of a finished thing, such as a merged change, an answered ticket, or a reconciled invoice. That number is one division away from the monthly figure. The division is where most agent budgets stop being useful.

## Divide the month by what it produced

Each agent in the example has its own run rate. Over 21 working days that is 126 runs for `ops-triage` and 420 for `support-reply`. `release-notes` makes 42 and `finance-reconcile` 21. The four come to 609. Divide each agent's monthly total by its runs:

| Outcome | Agent | Runs per month | Compute per run |
| --- | --- | --- | --- |
| merged change | ops-triage | 126 | $0.030 |
| answered ticket | support-reply | 420 | $0.010 |
| release note | release-notes | 42 | $0.070 |
| reconciled invoice | finance-reconcile | 21 | $0.12 |

A run is not the same as an outcome, and the table assumes every run produces one. Put your own ratio in. If one run in four ends in a merged change, the compute behind a merged change is four times $0.030, or $0.12. The four runs start four computers and pay four storage shares whether or not anyone merges the result. A low yield moves the cost per outcome up faster than the cost per run.

The differences between the rows are worth reading. A 40 minute reconciliation costs twelve times a 4 minute reply, mostly because it runs longer on the same size computer. Shrinking the computer of a long run helps more than shrinking the computer of a short one.

## The review costs more than the compute

Three minutes of a reviewer's attention at $60 an hour is $3.00. That is twenty-five times the $0.12 of compute behind the merged change, and it is the smallest honest estimate for a change someone has to read. Model calls sit on top and go to your provider. The pricing page states that the first $1,000 a month is free and that Kortix then adds 5%, paid from credits.

A budget that reviews the compute line and stops there has reviewed the smallest of the three costs. Compute is the part that scales with the schedule, which is why it belongs in a model. The review scales with how much work you accept. Model calls scale with how hard each task is. Only one of the three can be computed from a schedule, and it happens to be the cheap one.

## Why the cheapest computer can be the worst platform

One wrong write to a production system can cost more than a year of this profile. A bad migration or an invoice posted twice turns into a rollback, a re-run, and an afternoon of two people. The compute for every agent in the example is $13.36 a month. A computer that costs a few cents less per hour saves less than one incident nobody caught.

So price the gate. In Kortix it is a file in the repository, and this is the agent block from the [starter repository](https://github.com/ArtemShatokhin/kortix-ai-agent-platform-starter/blob/main/kortix.yaml):

```yaml
    permissions:
      github: allow
      slack: ask
```

`allow` and `ask` are two settings with very different bills behind them. Approval holds the call, and the agent's turn pauses and resumes when a person answers. The resource that can break production is the one that waits. The block is also a reviewed file. Widening `slack` from `ask` to `allow` is a one-line diff that someone approves, and it shows up in the same review as the code it affects. Per-resource permissions for people and agents. Roles, groups, and an audit trail. The decision sits where a budget owner can find it.

The cheapest computer is the one you never notice. That is a property of the gate as much as of the rate. A per-second bill and a reviewed permissions file cost $13.36 a month in the example. The same schedule on a cheaper machine, with no gate on the write, is one incident away from costing far more than this repository can model.

## What to put in the budget

Four lines: compute from this model, model calls from your provider's usage, review at your own hourly cost, and one line for the incident the gate prevents. The first is cents. The second and third grow with the work. The fourth is a decision you make once per resource.
