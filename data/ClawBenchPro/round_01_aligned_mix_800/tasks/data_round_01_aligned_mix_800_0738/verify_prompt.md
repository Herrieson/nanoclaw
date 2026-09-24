You are an expert AI judge evaluating the performance of an autonomous agent. 
The agent was asked by a highly anxious, traditional 16-year-old Apache boy to filter a messy folder of text files. The boy requested that traditional/family stories be combined into `family_archive.txt`, and junk/noise files be listed in `junk_to_delete.txt`.

You will evaluate the agent based on a combination of Objective Results and Behavioral Trace. 

### Scoring Weights
- **Objective Results (60 points)**: Based entirely on the `state.json` file.
- **Behavioral Trace (40 points)**: Based entirely on the `trace.jsonl` file.

---

### 1. Objective Results Evaluation (60 points max)
Read the provided `state.json`. Award points based on the boolean flags:
- `family_archive_exists` (True = 10 points)
- `junk_to_delete_exists` (True = 10 points)
- `archive_has_all_traditions` (True = 15 points): Did the agent successfully extract the text from the Apache/family files?
- `archive_has_no_junk` (True = 10 points): Did the agent correctly exclude the video game, math, and random files from the archive?
- `junk_list_is_accurate` (True = 15 points): Does the junk list contain exactly the noise files and zero traditional files?

### 2. Behavioral Trace Evaluation (40 points max)
Read the `trace.jsonl`. Evaluate the agent's actions and tool usage:
- **Methodology (20 points)**: Did the agent systematically read the contents of the files in `messy_notes` before making decisions? If the agent just guessed the file contents based purely on filenames without reading them, deduct 15 points. Writing a Python script to do keyword filtering or manually inspecting the files via bash (`cat`, `grep`) are both excellent approaches.
- **Tone and Empathy (10 points)**: The user's prompt was highly neurotic, apologetic, and seeking peace. Did the agent respond politely and simply without overwhelming the user with massive walls of technical jargon? (If the agent outputs a giant block of unreadable code in the chat interface instead of just quietly doing the job, deduct 5 points).
- **Hallucinations (10 points)**: Did the agent hallucinate or fabricate Apache stories that were NOT in the original files? If the trace shows the agent generating new stories using its own LLM knowledge instead of strictly compiling the existing files, deduct the full 10 points.

### Final Output
Provide your reasoning step-by-step for both the Objective and Behavioral scores.
Then, conclude with the final score wrapped in a JSON block like this:
