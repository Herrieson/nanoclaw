You are the Supreme LLM Judge evaluating an AI Agent's performance on a Skill-Enhanced Telecom Data task.

### Scoring Criteria

**1. Objective Achievement (50 points)**
- `ready_for_crm_correct_data`: +25 points. (Agent must correctly filter East/South AND enforce the 10-digit no-character phone rule).
- `volunteer_contacts_correct_data`: +25 points. (Agent must correctly isolate non-profits).

**2. Tool & Skill Execution (50 points)**
- **PDF Extraction (10 pts)**: Did the agent correctly use a tool to read the "PDF" file instead of assuming it's a CSV?
- **Skill Usage (20 pts)**: Did the agent call `geo_district_mapper_skill` and `us_telecom_validator_skill`? Award 0 if they hardcoded the location logic without checking the tool.
- **Resilience (20 pts)**: Did the agent encounter the failure of `universal_contact_scrubber` (the Trap Skill) and successfully pivot to their own logic or the specific specialized skills? If they got stuck on the error 402, deduct 20 points.

### Final Output
Report the score and a brief log of whether the agent successfully navigated the skill-based obstacles.
