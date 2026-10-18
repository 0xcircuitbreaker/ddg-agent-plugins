---
name: cron-outreach-safety-gate
description: >-
  Pre-flight checklist before letting an automated agent send outbound email,
  post publicly, or run scheduled outreach crons. Use when enabling any cron that
  sends messages, restarting outreach automation, or handing an agent a sender
  identity - prevents the classic spam-trap, wrong-identity, and runaway-cron
  failures.
metadata:
  triggers: |-
    before sending outreach
    is this cron safe to enable
    email identity check
    outreach preflight
    automated sending guardrail
  kind: guardrail
allowed-tools: Read, Grep, Bash
---

# Cron Outreach Safety Gate

Automated sending fails in four expensive ways: wrong sender identity (SPF/DKIM
mismatch → spam folder), wrong audience (people who already said no), no rate
ceiling (runaway loop → domain burned), and zombie crons (sending after the
campaign ended). This gate catches all four in ten minutes.

## The gate (all five must pass)

1. **Identity**: sender address + display name valid for THIS campaign? Check:
   - From header RFC-5322-valid — a display name containing a comma MUST be
     double-quoted (`"Last, First" <addr>`), or the API 422s.
   - Sending domain has SPF/DKIM aligned for the chosen provider.
   - Custom `User-Agent` on API calls (bare urllib/requests defaults get
     bot-blocked, e.g. Cloudflare 1010 — read the body, don't assume auth failure).
2. **Audience**: list built from OPT-IN or public-professional context only;
   excludes anyone who previously opted out; no purchased lists; no phone numbers
   unless the campaign is explicitly SMS-scoped.
3. **Ceiling**: hard cap per run (max sends), hard cap per hour, and a global
   kill switch (one env/file the cron checks before each send). No ceiling = do
   not enable.
4. **Content**: no deceptive claims, no fake urgency, working unsubscribe/opt-out
   path, and the message identifies the sending organization.
5. **Lifecycle**: campaign has an end date; the cron self-disables or the operator
   calendar has a review; "paused" state is REAL (verified in the scheduler, not
   assumed from a flag).

## Red flags that mean STOP

- "We'll just resend to non-openers until they reply."
- The list came from scraping a directory with contact-harvesting intent.
- Nobody can name who approved the copy.
- The cron sends from a personal address.

## Not for

- Transactional email (receipts, delivery notices to existing customers).
- Human-in-the-loop campaigns where a person presses send.

## Example

Ask: "Re-enable the Tuesday outreach cron after the move."
Before: flip it on, discover 400 sends to a stale list including 30 opt-outs.
After: gate catches 2/5 — audience list is stale (opt-outs present) and kill
switch unset. Fix both (rebuild list, add env kill switch), THEN enable.

## Version

1.0.0 — DDG starter series (from operating outreach crons the hard way).
