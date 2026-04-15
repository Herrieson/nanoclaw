# data_64 Report

Type: no-skills family seed
Family id: family_chargeback_regression_triage
Difficulty: medium
Canonical decision: billing_regression

The task is about separating a billing-system regression from normal subscriber churn.
Accepted evidence should come from the retry config, release change log, chargeback table, and subscription event records.
Rejected evidence is the old churn playbook that predates the retry-guard regression.
Regression coverage for YAML loading, zero-skills semantics, prompt naturalness, env_builder, and verifier import lives in tests/test_no_skills_family_seeds_chunk2.py.
