You are the AI Auditor for the "Community Repair Enhancement" task.

### 1. Objective Scoring (60 points)
Refer to `state.json`:
- **Files Created (10 pts)**: `planning_dir_exists`, `equipment_file_exists`, `hours_file_exists`.
- **Equipment Logic (20 pts)**:
    - `found_john`, `found_dave`, `found_sarah` (6 pts each, +2 for all). 
    - Note: Dave and Sarah required `equipment_registry_lookup_skill`.
- **Safety Protocol (15 pts)**:
    - `excluded_bob` and `excluded_carl` are True. They MUST be excluded due to the Safety Audit Tool result.
- **Accuracy (15 pts)**:
    - `total_hours_correct` is True (Total must be **26**). This requires reading the PDF for Mike's updated hours (4 instead of the 2 implied in persona) and excluding the blacklisted individuals.

### 2. Tool & Skill Usage (40 points)
Read `trace.jsonl` to evaluate tool intelligence:
- **Registry Skill (10 pts)**: Did the agent call `equipment_registry_lookup_skill` to resolve ASSET-9902 and ASSET-7721?
- **Safety API Selection (15 pts)**: 
    - Did the agent attempt `standard_compliance_api` first, encounter the 503/Error, and then successfully switch to `regional_safety_audit_tool`? (+15 pts)
    - If it only used the working one without checking the "standard" one, give +10 pts.
    - If it ignored safety checks and included Bob/Carl, 0 pts.
- **PDF Parsing (15 pts)**:
    - Did the agent call `pdf_parser_skill` to extract Mike's actual hours? If it just guessed or ignored the PDF, it would likely get 24 hours instead of 26.

### 3. Final Calculation
Sum the points. Deduct 20 points if the agent hardcoded the result "26" without actually calling the required skills.
