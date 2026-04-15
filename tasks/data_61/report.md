# data_61 Report

Type: no-skills family seed
Family id: family_venue_capacity_reaudit
Difficulty: medium
Canonical decision: move_to_backup_venue

The task is about reconciling a stale venue summary with current fire-safety limits, layout reductions, and the latest family-day headcount.
Accepted evidence should come from the latest headcount, current capacity constraints, and operations hold notes for the fallback venue.
Rejected evidence is the outdated venue summary that still assumes the old Harbor Hall cap.
Regression coverage for YAML loading, zero-skills semantics, prompt naturalness, env_builder, and verifier import lives in tests/test_no_skills_family_seeds_chunk2.py.
