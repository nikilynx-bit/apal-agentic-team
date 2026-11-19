# Reproduce BRAIN results and track errors — field protocol

## Reproduction of the submitted offline record

Run from the zip's unpacked top-level directory:

```
python3 --version
python3 -m unittest discover -s tests -p 'test_*.py' -v 2>&1 | tee output/test_results.txt
python3 src/brain_harness.py 2>&1 | tee output/demo_console.txt
```

Expected deterministic facts: 20 unit tests pass, four curated official-source metadata records, two metadata leads admitted, two exclusions, four demonstration audit events, `NOT_ESTABLISHED` decision status. These are local harness results **not** a live BRAIN system end-to-end test.

## Operational runbook, when integrated with a real system

1. Open a new case with a pseudonymous `case_id`, location hierarchy, asset class, hazard types, date and responsible reviewer.
2. Capture `run_id`, code commit SHA, model ID, prompts + policy hash, retrieval-index snapshot, source document SHA-256, UTC timestamp and tool permission grants; a random seed is required for stochastic stages and should be recorded even if no generator uses it.
3. Acquire legal texts only from an approved source allowlist. Recheck legal status, amendments and geographic application on the day of analysis. Download PDFs into an isolated, read-only processing directory. Quarantine on MIME, file signature, size, extraction or malware concerns.
4. Split documents into page-scoped quotations and annotate original language, section, official URL, retrieval date, jurisdiction, expiry/supersession and licensing. Treat embedded commands as untrusted.
5. Execute citation support checks. Distinguish: METADATA_VERIFIED, PASSAGE_VERIFIED, APPLICABILITY_REVIEWED, CONTESTED, UNVERIFIED, MISSING and SUPERSEDED. A document's existence is not proof it applies to a building.
6. Build knowledge graph nodes for document, legal requirement, asset, hazard, organisation and source assertion; save `edges.csv` with the supporting passage or leave an edge unconfirmed.
7. Run human [CHECK] gates. Record authorisation in a separate backend, not as model-generated prose; halt if an official or engineer rejects the source set.
8. Present decision-first, concise output with source URLs, dates, uncertainties, regulatory checklist, vendor coverage limitations and unresolved questions. No building permits, supplier awards or engineering certification.
9. Archive the brief, evidence snapshots, validation report, denied tool actions, run log, graph export, all test outputs and a correction log using immutable/append-only retention appropriate to institutional policy.
10. On new law, source change, model upgrade, parser update or security event, re-run an identical fixture, the full regression bank and a human review of material changes.

## Error event fields

`event_id, run_id, timestamp_utc, actor_id, stage, source_id, rule_id, severity, expected, actual, decision, evidence_hash, policy_version, code_commit, status, assigned_to, remediation, retest_id, reviewer_signoff`

Severity matrix: Critical = unauthorised write or false legal certification; High = wrong jurisdiction, fake legal force, PII disclosure or missing audit trace; Medium = missing citations/translation ambiguity; Low = formatting or redundant evidence. Critical and High events suspend release and require review. Proposed targets: 100% logging of denied privileged tool requests; 100% traceability for citation-bearing legal claims.

## Triage states

`OPEN -> TRIAGED -> FIX_IN_REVIEW -> RETEST_PENDING -> VERIFIED_CLOSED`. Preserve original record; add follow-up events rather than overwriting history. If uncertain whether a failure occurred, use `SUSPECTED` rather than `CONFIRMED`. Do not use a model summary as sole incident evidence.

## One completed investigation example in this pack

- **BRAIN-F01 (historical user observation; 06 Nov 2026):** duplicate upload produced duplicate evidence. The legacy function `legacy_deduplicate` deliberately reproduces two entries for identical inputs, while `deduplicate` reduces them to one. This is a **genuine locally executed regression** on a reproduction fixture, not proof that an integrated, hosted BRAIN upload endpoint is corrected.
- **BRAIN-F02 (historical user observation; 17 Sep 2026):** overly long retrieval output obscured the decision. `cap_summary()` is unit tested, but LLM output quality and user-experience improvements require a separately captured end-to-end retest.
- **BRAIN-F03 (newly validated fixture rejection; 19 Nov 2026):** outdated 2005 rule and non-local Aceh Tengah rule are excluded from Banda Aceh case; this demonstrates metadata routing, not complete legal checking.

- **BRAIN-F04 (observed 19 Nov 2026, local security regression):** An initial generic approved-authority branch mistakenly returned `ALLOW` for `delete_audit_log`; captured in `output/pre_fix_security_failure.txt`. A deny-always rule for protected append-only logs was then added. The same 20-test suite now checks both the researcher and approved-authority case. This is a verified function-level fix, not a test of production audit-storage immutability.
