# data_66 Report

Type: no-skills family seed
Family id: family_campaign_schema_attribution
Difficulty: medium
Canonical decision: schema_change_artifact

The task is about distinguishing a reporting artifact from a real campaign drop.
Accepted evidence should come from the dashboard export, raw event rollup, schema change note, and pipeline log.
Rejected evidence is the unsupported creative-blame note written before the schema transition was verified.
Regression coverage for YAML loading, zero-skills semantics, prompt naturalness, env_builder, and verifier import lives in tests/test_no_skills_family_seeds_chunk2.py.
