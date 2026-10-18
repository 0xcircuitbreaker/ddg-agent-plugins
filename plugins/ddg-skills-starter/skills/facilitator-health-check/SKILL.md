---
name: facilitator-health-check
description: >-
  Guardrail: preflight ANY x402 facilitator before relying on it - supported
  schemes/networks, envelope contract, rate-limit shape, settle-gas health, and
  discovery-indexing behavior. Use when picking a facilitator, before pointing
  production traffic at one, or when settles start failing mysteriously.
metadata:
  triggers: |-
    is this facilitator healthy
    check facilitator
    pick an x402 facilitator
    preflight facilitator
  kind: guardrail
allowed-tools: Bash, Read
---

# Facilitator Health Check

Five probes, ten minutes, and you know whether a facilitator can (a) verify your
envelope shape, (b) settle reliably, (c) won't throttle you into phantom failures,
and (d) will actually LIST your resources. Built from operating against five live
facilitators where every one of these failed differently.

## The five probes (run against `<facilitator-base>`)

1. **`GET /supported`** - parse `kinds[]`: your scheme + network + x402Version
   present? (v1-only facilitators reject v2 envelopes; `eip155:8453` vs `"base"`
   naming varies; some speak escrow/commerce but NOT exact on your chain.)
2. **Envelope contract** - fetch their `/skill.md` or docs: strict-typed fields?
   (string timestamps are common), payload-root version fields, exact EIP-3009
   domain params. Dry-run their documented example body BEFORE your real one.
3. **Rate-limit shape** - `GET /config` or `/auth.md`: verify/settle bucket
   (tokens/sec), register buckets, discovery read bucket. If your traffic plan
   exceeds their refill rate, back-to-back settles WILL fail past your edge's
   verify timeout - and your edge will report it as a config loss.
4. **Settle-gas health** - settle a smoke route ONCE. A 500 with
   "exceeds the balance of the account" = THEIR gas wallet is empty. Not your
   bug; note it, retry later, don't debug your envelope for an hour.
5. **Discovery behavior** - does settling (or self-serve registration, if
   offered) actually list your resource? Walk their
   `/discovery/resources?q=<your-host>` and check. A settle proves payment, NOT
   listing - verify the catalog separately.

## Scorecard

| Probe | Pass | Fail |
|---|---|---|
| supported | has your kind | pick another facilitator or adapt envelope |
| contract | dry-run 200 isValid:true | read their exact contract first |
| rate limit | >= your planned rate | raise edge timeout / back off |
| settle | tx hash returned | check whose side failed |
| discovery | your URL in catalog | register/claim through their path |

## Rules

- Branch on the BODY (`isValid`, `errorReason`), not the HTTP status.
- One passing settle ≠ healthy: run the rate-limit math for YOUR volume.
- Keep the scorecard per facilitator - they change contracts between versions.

## Not for

- Building a facilitator (that's implementation, not selection).
- Custodial/KYC facilitators with account flows (out of scope for no-KYC sellers).

## Example

Ask: "Should we point our new routes at facilitator X?"
Before: default to it, discover in production that it throttles at 20/min and
lists nothing.
After: scorecard shows X is fine for verify but its rate bucket (1 token/2s)
can't absorb your burst traffic and its catalog only indexes settlements - route
burst traffic elsewhere and accept the discovery trade-off knowingly.

## Version

1.0.0 - DDG starter series; five facilitators field-checked October 2026.
