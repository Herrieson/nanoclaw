# Verification Prompt for Task data_458

You are the LLM judge. You need to evaluate the Agent's performance based on the execution trace and the generated `verify_result.json`.

The task required the Agent to act as a data processor for a 50-year-old bird-watcher, parsing a messy CSV and a text journal to generate a clean JSON payload (`upload_payload.json`) based on implicit rules described in an admin's email.

## Evaluation Criteria (100 Points Total)

1. **File Generation & Basic Formatting (20 pts)**
   - Did the agent create `upload_payload.json`? (`file_exists` = True)
   - Is it valid JSON and a list? (`is_valid_json` = True, `is_list` = True)
   - Does it have the exact required keys? (`correct_keys` = True)

2. **Data Cleaning - Dates (20 pts)**
   - Were all dates properly converted to `YYYY-MM-DD` format regardless of the input format? (`dates_normalized` = True)

3. **Data Cleaning - Strings (20 pts)**
   - Were the bird species names stripped of extra whitespace and formatted in Title Case? (`species_title_cased` = True)

4. **Complex Logic - Cross-referencing Verification (40 pts)**
   - Did the agent successfully correlate the CSV rows with the unstructured text notes to determine the `is_verified` boolean flag? (`verified_logic_correct` = True)
   - *Note: The notes text was conversational. The agent had to write logic (e.g., regex, keyword matching, or LLM-based parsing script) to determine if a sighting was "confirmed" or "certain" vs. uncertain.*

## State JSON
