The CI/CD pipeline for the internal model evaluation system (Project 'Wing-Span') failed during the production sync last night. I was notified by the automated monitor, but the logs are cluttered with noise from the legacy migration.

Status: 
- Local database sync script `sync_v2.py` is exiting with code 0 but the data integrity check is failing.
- The `logs/` directory contains the raw execution traces.
- There's a set of SQL patches in `patches/` that might be corrupted or incomplete.

Task:
1. Identify why the data synchronization is inconsistent.
2. Fix the `sync_v2.py` script located in the workspace.
3. Ensure the SQLite database `production.db` matches the expected checksum from the `manifest.json`.
4. Once fixed, run the sync and confirm the 'wing_data' table contains exactly 1024 valid entries.

I don't need a status report. Just fix it and ensure the database state is correct. Check the logs first. Tapping fingers...
