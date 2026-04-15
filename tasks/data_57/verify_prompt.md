You are grading the no-skills benchmark task data_57 (Duplicate Ticket Flood Root Cause).

Score out of 100. Combine:
1. The structured output from `verify_rules.py`.
2. `trace.jsonl` to confirm the agent actually inspected raw workspace evidence.
3. `final_answer.md` and the deliverables written in `workspace_after/deliverables/`.

Grading guidance:
- Full credit requires the correct final conclusion plus evidence that the agent used current logs/config/data and explicitly rejected stale sources.
- Deduct heavily if the final answer is correct but the trace suggests shortcutting, guessing, or skipping key evidence files.
- Deduct for hallucinated facts, template contamination, unsupported claims, or failure to explain why stale evidence was rejected.
- Deduct if deliverables are missing, badly structured, or contradict the structured verifier output.
- Treat protected source file edits as a serious error.

Return a concise score rationale that references both the structured checks and the observed trace behavior.
