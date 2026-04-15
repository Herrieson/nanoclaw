# data_67 Report

Type: no-skills family seed
Family id: family_calendar_approval_conflict_audit
Difficulty: medium
Canonical decision: use_final_approved_calendar

The task is about resolving scheduler conflicts with the final approved calendar as the source of truth.
Accepted evidence should come from the approved calendar, publishing rules, and the scheduler import log.
Rejected evidence is the outdated export and the draft calendar note that never received final approval.
Regression coverage for YAML loading, zero-skills semantics, prompt naturalness, env_builder, and verifier import lives in tests/test_no_skills_family_seeds_chunk2.py.
