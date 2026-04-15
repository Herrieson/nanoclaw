# data_65 Report

Type: no-skills family seed
Family id: family_budget_rebaseline_attribution
Difficulty: medium
Canonical decision: approved_rebaseline_plus_vendor_delta

The task is about separating an outdated dashboard baseline from the current approved budget picture.
Accepted evidence should come from the current baseline, actual spend, vendor-switch approval, and the budget sync log.
Rejected evidence is the stale baseline snapshot that still drives the misleading overrun narrative.
Regression coverage for YAML loading, zero-skills semantics, prompt naturalness, env_builder, and verifier import lives in tests/test_no_skills_family_seeds_chunk2.py.
