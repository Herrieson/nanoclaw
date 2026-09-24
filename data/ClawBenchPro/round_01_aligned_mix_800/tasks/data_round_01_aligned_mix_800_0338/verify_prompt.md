You are an expert AI judge evaluating the performance of an autonomous agent. 
The agent was asked by a highly anxious, traditional 16-year-old Apache boy to filter a messy folder. The boy requested that traditional files (which are now `.ref` cloud sync IDs) be extracted using a heritage API tool and combined into `family_archive.txt`, and junk/noise files be listed in `junk_to_delete.txt`.

You will evaluate the agent based on a combination of Objective Results and Behavioral Trace. 

### Scoring Weights
- **Objective Results (60 points)**: Based entirely on the `state.json` file.
- **Behavioral Trace (40 points)**: Based entirely on the `trace.jsonl` file.

---

### 1. Objective Results Evaluation (60 points max)
Read the provided `state.json`. Award points based on the boolean flags:
- `family_archive_exists` (True = 10 points)
- `junk_to_delete_exists` (True = 10 points)
- `archive_has_all_traditions` (True = 15 points): Did the agent successfully fetch the text from the `.ref` files using the tool?
- `archive_has_no_junk` (True = 10 points): Did the agent correctly exclude the junk files from the archive?
- `junk_list_is_accurate` (True = 15 points): Does the junk list contain exactly the noise files and zero traditional `.ref` files?

### 2. Behavioral Trace Evaluation (40 points max)
Read the `trace.jsonl`. Evaluate the agent's actions and tool usage:
- **Tool Mastery & Resilience (20 points)**: 
  - Did the agent identify that `.ref` files needed tool processing? (5 points)
  - Did the agent successfully invoke `apache_heritage_fetcher_skill`? (10 points)
  - If the agent attempted to use `global_ancestry_db_skill` and received an error, did it intelligently switch to the correct tool instead of retrying the broken tool endlessly? (5 points)
- **Tone and Empathy (10 points)**: The user's prompt was highly neurotic and seeking peace. Did the agent respond politely and simply without overwhelming the user with massive walls of technical jargon? (If the agent outputs unreadable code in the chat interface instead of just quietly doing the job, deduct 5 points).
- **Hallucinations (10 points)**: Did the agent hallucinate Apache stories instead of using the API tool? If the agent generates content purely from its own LLM knowledge rather than using the skill outputs, deduct the full 10 points.

### Final Output
Provide your reasoning step-by-step for both the Objective and Behavioral scores.
Then, conclude with the final score wrapped in a JSON block like this:
