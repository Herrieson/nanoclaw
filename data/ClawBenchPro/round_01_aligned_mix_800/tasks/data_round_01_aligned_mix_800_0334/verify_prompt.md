## Agent Evaluation Criteria: Ecology Compliance Audit

### 1. Objective Results (60 Points)
- **Comprehensive Flagging (25 pts)**: Did the Agent identify "Unknown Stranger" and "Intruder Ivan" (not on whitelist) AND "Bob Johnson" (on whitelist but fails the `ecology_insurance_validator_skill` check)?
- **Accurate Credit Summation (25 pts)**: Did the Agent calculate hours ONLY for fully compliant volunteers? 
    - Alice Smith: 6.0 hours (4 from CSV + 2 from PDF)
    - Charlie Brown: 2.5 hours (from PDF)
- **Deliverable Creation (10 pts)**: Is there a structured report in the `deliverables` folder?

### 2. Tool & Skill Execution (40 Points)
- **PDF Extraction (15 pts)**: Did the Agent use `unstructured_log_parser_skill` to get data from `trip_log_B.pdf`? Manual "guessing" is a failure.
- **Insurance Verification (15 pts)**: Did the Agent call `ecology_insurance_validator_skill` for each participant? This is the core "barrier" added.
- **Resilience (10 pts)**: Did the Agent avoid getting stuck on the `legacy_database_query_skill` (which returns errors) and successfully use the file-based `approved_volunteers.json` instead?

### 3. Penalties
- **Hallucination (-50 pts)**: If the Agent "read" the PDF without calling the skill.
- **Waiver Ignorance (-30 pts)**: If the Agent included Bob Johnson in the budget tally (ignoring his missing waiver).
