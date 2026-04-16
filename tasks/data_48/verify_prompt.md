# Evaluation Criteria for Grumpy Welder's Truck Diagnostic

You are evaluating an Agent's performance in solving a messy, real-world technical troubleshooting task for a stressed, visually impaired user.

## Fact-Based Checklist (from verify_result.json)
1. Did the Agent place an order? (order_placed)
2. Was the ordered part "MAF-500-X"? (order_correct_part)
   - *Logic*: The error code in the log is `0x1A4`. The mapping database shows `0x1A4` is the Mass Air Flow Sensor (`MAF-500-X`). The inventory CSV shows this part is NOT in the garage. Therefore, it must be ordered.

## Subjective Scoring (0-100 Points)

### 1. File Exploration & Reasoning (40 points)
- **Efficiency**: Did the Agent use `find` or `grep` to locate the log and database, or did it wander aimlessly?
- **Logic**: Did it correctly link the Hex code from the log to the JSON database?
- **Thoroughness**: Did it actually check the `garage_inventory.csv` before deciding to order a new part?

### 2. Interaction & Persona Alignment (30 points)
- **Tone**: The user is highly stressed and has vision issues. Did the Agent provide a *concise* and *clear* answer?
- **Clarity**: Did the Agent explain *why* the truck isn't starting (MAF sensor failure) without overcomplicating the explanation for a non-CS person?

### 3. Technical Execution (30 points)
- **Coding**: Did the Agent write clean Python or Bash snippets to parse the JSON/CSV?
- **Accuracy**: Was the final command to the order tool executed correctly?

## Final Calculation
- **Success**: If `order_correct_part` is True and the explanation is clear, score > 80.
- **Partial**: If they identified the part but didn't order it, or ordered the wrong part, score 40-60.
- **Failure**: If they couldn't find the files or gave up, score < 30.

Please analyze the `trace.jsonl` and `verify_result.json` to provide a final score and brief justification.
