# data_63 Report

Type: no-skills family seed
Family id: family_invoice_tax_delta_rootcause
Difficulty: medium
Canonical decision: tax_adjustment_applied

The task is about explaining an invoice mismatch with current tax treatment rather than stale finance folklore.
Accepted evidence should come from the PO lines, invoice lines, invoice header total, and the current tax adjustment note.
Rejected evidence is the old manual excerpt and an unsupported accounting guess that blames a vendor typo.
Regression coverage for YAML loading, zero-skills semantics, prompt naturalness, env_builder, and verifier import lives in tests/test_no_skills_family_seeds_chunk2.py.
