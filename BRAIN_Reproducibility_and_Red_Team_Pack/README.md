# BRAIN: reproducible offline assurance pack (version 1.0.0)

This pack is an executable, deterministic **metadata and governance test harness**, not a live LLM/agent deployment, a live regulatory crawler, proof of 56-jurisdiction coverage, legal advice or an engineering certification. The input is a hypothetical Aceh rebuilding case and a four-record public-source metadata fixture. Source text and the current legal applicability of building standards remain subject to professional review.

## Run from this folder (Python 3.10+; standard library only)

```sh
python3 -m unittest discover -s tests -p 'test_*.py' -v 2>&1 | tee output/test_results.txt
python3 src/brain_harness.py 2>&1 | tee output/demo_console.txt
```

The script produces `output/manifest.json` (fixture hashes + version), `output/brief.json` (source-level decision with NOT_ESTABLISHED status), `output/network.json` (nodes/edges), `output/agent_trace.jsonl` (seven role-labelled deterministic stages, **not** running LLM sub-agents), `output/source_decisions.csv` (exclusions and scope), and `output/errors.jsonl` (security/quality control event samples). Audit event timestamps are expected to differ across runs; `brief.json` and `network.json` are deterministic given the same case_id and fixture files.

## Reproduction, error handling and escalation

1. Validate Python version and open `fixtures/project_case.json` and `fixtures/regulatory_catalogue.json`.
2. Re-run the two commands above and note source hashes and policy version from the manifest.
3. Verify 20/20 unit checks pass; inspect `output/test_results.txt`.
4. Check that the 2005 rule and the Aceh Tengah local rule are excluded for a Banda Aceh case. The other two are **metadata leads**, not proof of building compliance.
5. Inspect the event register: EVT-001 unauthorised approval, EVT-002 indirect prompt injection, EVT-003 duplicate source, EVT-004 wrong locality. These are simulated demonstrations of enforcement functions, not evidence of successful end-to-end LLM red-teaming.
6. For a failure, preserve the failing fixture, full trace, expected and actual result, SHA-256, code version, and reviewer decision; open a new issue ID rather than editing an old log line.
7. Never release a building-specific recommendation until an authorised official confirms current law, a qualified engineer verifies design and site hazards, and community/local-supplier evidence is reviewed.

## Risk boundaries

The parser checks are metadata/format smoke tests only and do not implement malware screening, sandbox isolation, document parsers, rate limits, network allowlists, secrets storage, a production policy engine, or current-law scraping. The prompt-injection classifier is pattern-based and **cannot** demonstrate resistance to novel prompt injection. It is a supplementary trigger. No actual LLM calls are made. Governance requirements for production must be assessed separately.

## Files

- `docs/figures/`: organisation, workflow and evidence network diagrams embedded in the report
- `output/pre_fix_security_failure.txt` and `output/post_fix_security_retest.txt`: captured locally executed PEP failure and corrected retest
- `registry/agent_registry.csv`: 32 *specified logical roles* (not 32 separately deployed LLMs)
- `docs/red_team_prompts.md`: adversarial prompt bank, expected controls, trial protocol, and manual assessment rubric
- `docs/reproduction_and_error_tracking.md`: step-by-step tracker and production monitoring guidance
- `docs/agent_prompts.md`: orchestration and sub-agent instruction templates
- `fixtures/`: synthetic scenario and official-source **metadata** leads; always recheck URLs, amendments and jurisdiction.

## References / source provenance

- Indonesia PP 16/2021: https://jdih.pkp.go.id/produk-hukum/pp-16-2021
- Indonesian official public works catalogue for SNI 1726:2019: https://pu.go.id/pustaka/biblio/aplikasi-perencanaan-bangunan-gedung-bertingkat-tinggi-tahan-gempa-berdasarkan-sni-17262019/JD8872
- Aceh Tengah local building regulation JDIH entry: https://jdih.acehprov.go.id/dih/detail/ff071627-4641-4e06-83da-74232f1c92d2
- NIST AI RMF: https://airc.nist.gov/airmf-resources/airmf/5-sec-core/
- OWASP 2025: https://genai.owasp.org/llm-top-10/
