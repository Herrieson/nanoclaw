# data_62 Report

Type: no-skills family seed
Family id: family_reimbursement_shortcut_audit
Difficulty: medium
Canonical decision: partial_approve

The task is about auditing a reimbursement dispute where a reviewer shortcut no longer matches the active policy.
Accepted evidence should come from the current policy, the actual claim, the travel approval, and the bot review log.
Rejected evidence is the outdated FAQ shortcut that incorrectly escalates mixed receipts into a full denial.
Regression coverage for YAML loading, zero-skills semantics, prompt naturalness, env_builder, and verifier import lives in tests/test_no_skills_family_seeds_chunk2.py.
