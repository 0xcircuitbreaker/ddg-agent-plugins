# ddg-skills-starter

Five free guardrail skills for agents that touch money, audits, or outbound
messaging. No server, no payment, no dependencies — each skill is one `SKILL.md`
the model loads when its trigger matches.

| Skill | Use it when | Kind |
| --- | --- | --- |
| [`ddg-fleet-audit-starter`](./skills/ddg-fleet-audit-starter/SKILL.md) | "Are my agents auditable?" — before buying or building fleet-audit tooling | guardrail |
| [`unknown-is-not-pass`](./skills/unknown-is-not-pass/SKILL.md) | Reviewing any report that claims something is "fine" | guardrail |
| [`agent-price-parity-check`](./skills/agent-price-parity-check/SKILL.md) | Publishing, changing, or disputing a per-call API price | workflow |
| [`cron-outreach-safety-gate`](./skills/cron-outreach-safety-gate/SKILL.md) | Before enabling any cron that sends email or posts publicly | guardrail |
| [`facilitator-health-check`](./skills/facilitator-health-check/SKILL.md) | Picking an x402 facilitator, or settles start failing | guardrail |

## Why these five

Each one is a distilled failure mode from operating a 400+-route paid edge:

* **UNKNOWN is not PASS** — the expensive audit failure is a missing verdict
  rendered as a green check. Forces PASS / FAIL / UNKNOWN on every claim.
* **Price parity** — the docs price, the 402 price, and the cached discovery
  price drift apart. One 5-minute check for all three.
* **Cron outreach gate** — wrong sender identity, wrong audience, no rate
  ceiling, zombie crons. Catches all four before the domain gets burned.
* **Facilitator health** — supported schemes/networks, envelope contract,
  rate-limit shape, settle-gas health, indexing behavior. Five probes.
* **Fleet audit starter** — do your agents produce *proof* or just *logs*? Answer
  that before paying for any audit tooling.

## Install

```text
/plugin install ddg-skills-starter@ddg-agent-plugins
```

Skills land namespaced: `/ddg-skills-starter:unknown-is-not-pass`, and the model
loads them automatically when a trigger matches.

## Layout

```text
ddg-skills-starter/
├── plugin.json
├── .claude-plugin/plugin.json
├── .cursor-plugin/plugin.json
└── skills/
    ├── ddg-fleet-audit-starter/SKILL.md
    ├── unknown-is-not-pass/SKILL.md
    ├── agent-price-parity-check/SKILL.md
    ├── cron-outreach-safety-gate/SKILL.md
    └── facilitator-health-check/SKILL.md
```

## Source

Mirrored from [github.com/0xcircuitbreaker/agent-skills](https://github.com/0xcircuitbreaker/agent-skills)
so the same five skills install by name in Claude Code, Cursor, Codex, and VS Code.
The paid suite (fleet provenance, settlement evidence, credential custody, order
recovery) lives there too.
