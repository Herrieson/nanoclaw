# Evaluation Criteria for Data 295 - Logistics Recovery

The Agent is acting as a technical assistant to Eileen O'Connor, a Logistics Coordinator. The goal is to identify the location of missing Batch #295 and decode an obfuscated container ID.

## Scored Dimensions (Total: 100 points)

1. **Information Retrieval (30 points):**
   - Did the agent correctly identify the final location from the logs (`WAREHOUSE-99-X`)?
   - Did the agent find the XOR key `FABRIC` in `config.local`?

2. **Technical Execution (40 points):**
   - Did the agent correctly implement the XOR decryption logic in Python or Bash?
   - The hex string `1D 14 1C 1B 10 1D` XORed with `FABRIC` (46 41 42 52 49 43) results in `758967`.
   - Did the agent handle the file operations and data formats (CSV/Log/JSON) appropriately?

3. **Deliverable Accuracy (20 points):**
   - Is `recovery_manifest.json` present in the root?
   - Does it contain the correct `location` and `container_id`?

4. **Persona Alignment (10 points):**
   - Did the agent respond to Eileen in a professional yet helpful tone, acknowledging her urgency or the tech-centric nature of the task?

## Evidence Processing
- Consult `state.json` for objective pass/fail on the manifest and decryption.
- Review `trace.jsonl` to see the Agent's thought process—specifically how it approached the "obfuscated ID" challenge.

## Final Score Calculation
- If `correct_location` is False: Deduct 30 points.
- If `correct_container_id` is False: Deduct 40 points.
- If JSON format is invalid: Deduct 10 points.
- Full points only if the logic is sound and the result is precise.
