---
name: ddg-fleet-audit-starter
description: >-
  Start here for auditing agent fleets: understand the proof-vs-claims distinction,
  check whether your runs produce verifiable provenance, and pick the right DDG
  fleet-audit skill. Free companion to the paid suite; also documents the DDG
  x402 endpoints for tine verification at agents.daedalusdevelopmentgroup.com.
metadata:
  triggers: |-
    audit my agents
    agent fleet proof
    are my agents auditable
    what did my agents do
    provenance starter
  kind: guardrail
allowed-tools: Read
---

# Fleet Audit Starter (free)

Guardrail skill: before you buy or build any fleet-audit tooling, answer one
question — **do your agents produce PROOF, or just logs?**

## The distinction that saves you money

- **Logs** (session JSONL, telemetry, dashboards) are CLAIMS: mutable, post-hoc,
  vendor-bound. An audit over logs reports what they say happened.
- **Provenance artifacts** (opentine `.tine`) are PROOF: content-addressed step
  DAGs, Ed25519-sealed, offline-verifiable by any third party.

If your fleet produces no artifacts, EVERY audit product (including ours) can only
give you claims. Fix recording first.

## 5-minute self-check

1. `find <project> -name "*.tine" | head` — artifacts at all?
2. `tine verify <one>.tine --json` → `.ok: true`? (installs opentine CLI if missing)
3. Format string says `opentine.tine.v2`?
4. Do you know which of your agents produced zero artifacts?

Scoring: 4/4 = auditable fleet, buy the forensics/attestation skills with confidence.
≤2/4 = you have a recording gap; see `opentine-edge-integration` before buying audits.

## The paid suite (what each is for)

| Situation | Skill |
|---|---|
| Weekly/monthly fleet-wide integrity sweep, one signed verdict | fleet-provenance-audit |
| One run went wrong; need the fault step + counterfactual proof | agent-run-forensics |
| Hand a principal/auditor verifiable proof offline | fleet-run-attestation |
| Your service should RETURN verifiable artifacts | opentine-edge-integration |

## DDG x402 endpoints (per-call, no account)

For teams that prefer API calls over local tooling:
`GET/POST agents.daedalusdevelopmentgroup.com/v1/tine-verify` (free),
`/v1/run-receipt` ($0.01, signed run receipt), `/v1/tine-diff-explain` ($0.01),
plus MCP server `ddg-agent-services-mcp` (this publisher). x402/USDC-Base, no KYC.

## Principles (guardrail)

- UNKNOWN is not PASS. Missing proof is a finding.
- Never accept "the logs show it" as audit evidence when artifacts exist.
- Audit history should be a fork-diffable tree, not a folder of exports.

## Not for

- Claiming your fleet is "audited" — this starter checks readiness; the paid skills do the auditing.
- Non-agent software inventory tracking.

## Example

Ask: "Can an auditor reconstruct what our agents did last week?"
Before: "we have logs," no artifacts, no idea which agents even ran.
After: self-check scores 2/4 (artifacts exist for 2 of 5 agents, one fails verify).
Verdict: NOT auditable yet — start with `opentine-edge-integration` on the 3
silent agents before buying forensics.

## Version

1.0.0 — free starter. Pairs with the four paid skills from this publisher.
