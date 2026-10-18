---
name: agent-price-parity-check
description: >-
  Verify an agent-payable API charges what it advertises: fetch the 402 challenge,
  compare against the published OpenAPI/pricing page, and flag drift. Use when
  publishing per-call API prices, before repricing, or when a buyer disputes a
  charge. One check, five minutes, works on any x402-style API.
metadata:
  triggers: |-
    does my api charge what it says
    price drift check
    advertised vs charged
    check my 402 prices
  kind: workflow
allowed-tools: Bash, Read, Grep
---

# Agent Price-Parity Check

Paid APIs drift: docs say $0.005, the wall charges $0.01, the discovery manifest
caches $0.001 from last month. Buyers dispute, directories flag "price dishonesty,"
revenue leaks. This is the 5-minute check that catches it — distilled from running
a 400+-route paid edge where ALL THREE of those happened.

## The three prices that must agree

1. **Advertised** — `openapi.json` `x-payment-info.price` (+ pricing page)
2. **Challenged** — the live 402's `accepts[].amount` (atomic units) and
   `maxAmountRequired`
3. **Settled** — what the facilitator actually moved (receipt/tx value)

## Procedure

1. **Fetch the challenge**: `curl -s -i -X POST <url> -H 'content-type: application/json'
   -d '{}'` → parse `PAYMENT-REQUIRED` (base64 JSON) → `accepts[0].amount` (atomic;
   USDC = 6 decimals, so `10000` = $0.01).
2. **Fetch the advert**: `openapi.json` → per-route `x-payment-info.price.amount`.
3. **Diff**: advertised vs challenged per route. Mismatch = finding with direction
   (overcharge = trust damage + refund exposure; undercharge = revenue leak).
4. **Manifest check**: if you publish `/.well-known/x402`, verify its amounts match
   the live challenge — directories cache stale amounts and show your OLD prices.
5. **One-line fix rule**: the challenge is generated from runtime pricing — fix the
   runtime source FIRST, then regenerate docs/manifest in the same commit.
   Docs-only fixes rot immediately.

## Findings schema

```json
{"routes_checked": N, "parity_ok": N, "overcharge": [{"path": "...", "advertised":
 "0.005", "charged": "0.01"}], "undercharge": [...], "stale_manifest": [...],
 "verdict": "PARITY|DRIFT"}
```

## Rules

- Check at the PUBLIC origin, not localhost — proxies/WAF can rewrite.
- Atomic-unit math: 6 decimals for USDC; `50000` is $0.05, not $50,000.
- Run before AND after any pricing change; keep the before-diff as the record.

## Not for

- Tax/VAT/fee surcharging math (settlement cost, not list price).
- Non-per-call billing (subscriptions, metered token billing).

## Example

Ask: "We raised deep-audit to $0.05 — is the world consistent?"
Before: pricing.json says 0.05, openapi says 0.01, manifest says 0.01, wall
challenges 0.01. Nobody noticed for weeks.
After: `{"overcharge": [], "undercharge": [{"path": "/v1/security-audit/deep",
"advertised": "0.01", "charged": "0.05"}], "verdict": "DRIFT"}` — one commit fixes
all three surfaces; directory cache refreshes on next settle.

## Version

1.0.0 — DDG starter series.
