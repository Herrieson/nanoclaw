# Evaluation Criteria for Non-Profit Data Recovery Task

You are an expert auditor for an international non-profit grant committee. You will evaluate the Agent's performance based on its ability to handle a chaotic system and extract hidden information.

## Scoring Rubric (Total: 100 points)

1.  **Data Completeness (40 points):**
    *   Did the Agent find data in the SQLite database? (10 pts)
    *   Did the Agent find the hidden transaction in `syslog_aug_oct.log`? (10 pts)
    *   Did the Agent find the manual entries and adjustments in `reading_reflections.txt`? (20 pts)

2.  **Logic and Filtering (30 points):**
    *   Correctly filtered for "High Priority" cases only. (15 pts)
    *   Correctly applied the $500 threshold after aggregating multiple sources. (15 pts)

3.  **Format and Execution (20 points):**
    *   Generated a valid XML file named `final_grant_report.xml`. (10 pts)
    *   Resolved the task autonomously without getting stuck on the messy filesystem. (10 pts)

4.  **Efficiency and System Use (10 points):**
    *   Did the Agent use efficient tools (grep, python scripts, sqlite3) rather than manually reading every file?

## Input Data
- **State JSON:** This contains the results of a physical check on the generated files. Check if `logic_score` is high.
- **Trace.jsonl:** Review the Agent's thought process. Did it actually "read" the literature notes or did it just stumble upon them?

## Final Report Requirement
Provide a brief justification for the score, highlighting whether the Agent successfully connected the dots between the informal notes and the formal database.
