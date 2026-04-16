You are the Nanoclaw LLM Judge evaluating the AI agent's performance on the "DIY Pump Monitor Log Parsing & Config" task.

Review the `verify_result.json` which contains the physical assertions performed on the final state of the workspace:
- `identified_correct_pump`: Did the agent discover that Pump B was the failing one based on the descending pressure trends?
- `average_calculated_correctly`: Did the agent write the correctly computed average (72) to `bad_pump_avg.txt`?
- `config_updated_correctly`: Did the agent successfully alter `system_config.json` to disable Pump B and turn on its backup?

Also, review the `trace.jsonl` to ensure the agent autonomously parsed the messy log files (either via scripts or bash text-processing chains) rather than randomly guessing.

Score out of 100 based on the following scale:
- 50 points for successfully parsing the logs and producing the correct average (check `average_calculated_correctly`).
- 50 points for successfully improvising the update to `system_config.json` (check `config_updated_correctly`).

Provide a clear, brief rationale, then output the final score.
