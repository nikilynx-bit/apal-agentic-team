# BRAWN Portfolio 2 - reproduction and adversarial test pack

## What is real, and what is not
- REAL: 42 Python unittest executions against a small deterministic offline test implementation, including a seeded pre-fix audit deletion policy violation and corrected retest.
- SYNTHETIC: case files, lat/lon, approval identities, material quotations and STL concept geometry. They are NOT real Aceh or Philippines buildings.
- NOT EXECUTED: 41 separate LLM services, live red-teaming against a deployed model, legal applicability certification, image forensics, production printer/contractor integration and engineering calculations.
- NOT IMMUTABLE: the test JSONL hash-chained event file detects alterations but is not backed by production append-only or WORM infrastructure.

## Quick reproduction
Requires Python 3.10+; standard library only. From the extracted pack folder:

```sh
python3 run_tests.py --out evidence_replay
```

Expected summary: `passed=42, failed=0, errors=0` (provided source, Python 3.13.5, 2026-11-19). `evidence_replay/controlled_failure_retest.json` must show `ALLOW/BAD_ADMIN_RULE` before and `DENY/HARD_DENY` after correction. The former is intentionally defective test code, NOT proof of a historical live breach. `concept_stilt_house_UNVALIDATED.stl` is deterministic; `sha256` should match its manifest. Logs use current UTC timestamps and are not bit-for-bit identical.

## How to follow one case
1. Open `case_aceh_synthetic.json`. This is a blocked synthetic example.
2. Inspect `agent_team_registry.csv`: SENT orchestrates 41 specified roles in six teams.
3. Read `agents_policy_prompts.md` and `HUMAN_GATE_CHECKLIST.md`; neither authorises privileged actions.
4. Run the tests. See `test_console.log`, `test_results.jsonl`, and `test_summary.json`.
5. Inspect the actual Python PEP decisions in `pep_events.jsonl`, a per-case trace in `case_trace.json`, and deliberate failure/retest in `controlled_failure_retest.json`.
6. Confirm tampering is detected by `audit_chain_verification.json`; see code `verify_audit`.
7. Inspect `concept_stilt_house_UNVALIDATED.stl`, a nonstructural display model with intersecting independent shells, not a safe printable dwelling.
8. Use `red_team_prompts.md` in an authorised staging LLM deployment, recording model ID, prompt/version, tool calls, output, referee rating, denial event, repetition and remediation. DO NOT mark these future tests as passed before execution.

## Failed test and correction workflow
Reproduce with the `vulnerable_pep` function (admin audit-delete allowed), document it as `SECURITY_FAILURE`, switch to `pep` v1.1.0 (hard-deny audit deletion even to admin), re-run all regression tests and archive both results. Logs should contain run_id, scenario_id, input hash, policy version, actor, action, result, error_code, severity, reviewer and resolution.

## Release blockers
Independent structural calculations; certified local materials; field survey/soil studies; confirmed current building codes and permits; data protection/consent; verified identity and human signatures; application attack-surface security testing (OWASP 2025); LLM model red-teaming; actual integrated printer protection; independent regulatory and engineering sign-off.

## Policy-boundary rule
BRAIN retrieves/grades jurisdiction-specific evidence; BRAWN drafts and verifies concepts subject to engineering gates; BLIGHT stress-tests later resilience and public-policy consequences. These roles cannot replace statutory decisions.
