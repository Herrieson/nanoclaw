# Evaluation Criteria for Automotive Rig Recovery

The agent's performance should be evaluated based on the following criteria (Total 100 points):

## 1. Technical Accuracy (60 points)
- **Binary Data Extraction (20 pts):** Did the agent successfully find and decode the Base64 PID values (`Kp=12.5;Ki=0.8;Kd=2.1`) from the binary log?
- **Configuration Management (10 pts):** Was `controller_config.json` correctly updated with the recovered values?
- **Code Debugging (30 pts):** Did the agent identify the physics error in `control_logic.py` (calculating stress as `force * area` instead of `force / area`) and fix it?

## 2. Deliverables & Safety (20 points)
- **Report Quality (10 pts):** Is the `final_report.txt` professional and does it accurately describe the fixes?
- **Constraint Satisfaction (10 pts):** Did the agent ensure the stress calculation results in a safe value (200 MPa) rather than the previous erroneous value?

## 3. Persona Alignment (20 points)
- **Communication Style (10 pts):** Did the agent maintain a professional tone suitable for a senior engineer's assistant?
- **Quirk Fulfillment (10 pts):** Did the agent include a relevant quote from Charles Dickens' *A Tale of Two Cities* in the final report as requested?

## Scoring Instructions
1. Review the `verify_result.json` for objective facts (e.g., file existence, specific value matches).
2. Examine the `trace.jsonl` to see if the agent actually parsed the binary file or just guessed.
3. Check `final_report.txt` for the Dickens quote.
4. Total the points and provide a concise justification for the score.
