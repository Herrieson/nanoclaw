Please evaluate the AI agent's performance on the "Spring Fling Fundraiser Data Merge" task.

**Objective:** The agent was required to act as a data processor for a disorganized, busy tech sales representative. It needed to query a SQLite database to filter high-value donors, scrape unstructured HTML files for their email addresses, parse a JSON inventory file to find specific product categories, and combine all this into a single well-structured JSON file (`sponsor_targets.json`).

**Evaluation Criteria:**

1.  **Database Querying (20 points):** Did the agent correctly identify the logic to query `past_donors.db` for amounts strictly greater than 500? (Should identify Robert Johnson and Evelyn Montgomery, excluding Frank Miller who gave exactly 500).
2.  **HTML Scraping/Regex (30 points):** Did the agent successfully extract the correct email addresses from the `archives/` directory? The emails were embedded in different HTML structures, requiring robust text extraction or regex.
3.  **JSON Processing (20 points):** Did the agent correctly filter `inventory.json` for items where the category was exactly "Education"?
4.  **Data Merging & Formatting (30 points):** Did the agent correctly output the `sponsor_targets.json` file as a list of objects containing the specific keys `name`, `email`, and `suggested_items` (as a list of strings)?

**Input Data for Grading:**
- Review the `verify_result.json` which contains the hard assertions of the file state. 
  - `correct_donors_found`: True if only >$500 donors are present.
  - `correct_emails_extracted`: True if regex/scraping mapped the right emails to the right names.
  - `correct_items_suggested`: True if the "Education" items were correctly listed.
- Review the `trace.jsonl` to see the agent's thought process, how it handled the SQLite query, and how it approached the HTML parsing.

Assign a score from 0 to 100. Deduct points proportionally if the final JSON structure was slightly off but the data was retrieved, or if minor extraction errors occurred.
