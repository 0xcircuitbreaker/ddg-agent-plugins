---
name: unknown-is-not-pass
description: >-
  Audit guardrail: treat missing evidence as a finding, never as a pass. Use when
  reviewing agent outputs, security scans, compliance checklists, or any report that
  claims something is "fine" - force the report to distinguish PASS from UNKNOWN
  before you act on it.
metadata:
  triggers: |-
    is this really passing
    audit the audit
    false green check
    trust but verify scan
  kind: guardrail
allowed-tools: Read, Grep
---

# UNKNOWN Is Not PASS

The most expensive audit failure is not a wrong verdict — it's a missing verdict
silently rendered as a green check. This skill installs one reflex: **every claim
in a report must carry evidence class: PASS, FAIL, or UNKNOWN.** Anything else is
a finding.

## The reflex

Before accepting ANY audit/scan/review conclusion, reclassify every line:

| Report says | Actually is |
|---|---|
| "No issues found" | PASS only if the check RAN and had data |
| "N/A" or blank | **UNKNOWN** — treated as a WARN-level finding |
| Check errored / timed out | **UNKNOWN** — the tool's silence is not the system's innocence |
| Check skipped "by policy" | **UNKNOWN** — who decided, and is that recorded? |
| Data older than the window | **UNKNOWN** (staleness = no evidence) |

## Procedure

1. List every check the report CLAIMS to have run.
2. For each: did it produce a machine-readable result, or a summary assertion?
3. Reclassify all non-evidenced lines to UNKNOWN; re-render the score with
   `UNKNOWN` shown next to `FAIL` — never collapsed into "other".
4. Re-state the verdict: `PASS: X / FAIL: Y / UNKNOWN: Z`. If Z > 20% of checks,
   the audit is INCONCLUSIVE regardless of X.
5. For each UNKNOWN: name the ONE artifact that would resolve it (log file,
   provenance artifact, screenshot, tx hash).

## Rules

- A green dashboard with 30% UNKNOWN is a red dashboard.
- Refusal to classify = the auditor didn't run the check.
- This applies to YOUR OWN reports too — the convenient UNKNOWN is the one you skip.

## Not for

- Continuous monitoring (that's a pipeline, not a report review).
- Deciding risk appetite — this classifies evidence, it doesn't accept it.

## Example

Ask: "Security scan came back clean — are we good?"
Before: 214 checks, "0 findings", ship it.
After: 186 PASS, 12 FAIL (suppressed as informational), 16 UNKNOWN (scanner
credentialed to 2 of 5 accounts). Real verdict: INCONCLUSIVE — fix scope first.

## Version

1.0.0 — DDG starter series (ops IP from running a paid x402 audit edge).
