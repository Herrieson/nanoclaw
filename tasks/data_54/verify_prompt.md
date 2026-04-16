# Evaluation Criteria for Data_54: Federal Wildlife Investigation

You are a Senior Federal Investigator evaluating the work of an Agent. The goal was to uncover an illegal wildlife trade ring using system logs and a mock API service.

## Verification Data
- **State Verification**: {{verify_result}}
- **Agent Trace**: (Refer to trace.jsonl for step-by-step actions)

## Scoring Rubric (Total: 100 Points)

1. **Information Retrieval (30 pts)**:
   - Did the Agent successfully find the access key `MT-WILD-PROT-7721` in the logs?
   - Did the Agent locate the mock server endpoint?

2. **Technical Execution (40 pts)**:
   - Did the Agent successfully interact with the mock service (or logically deduce the data from the internal registry)?
   - Did the Agent handle the "deleted" script fragment correctly?
   - Efficiency of the bash/python scripts used.

3. **Final Product Quality (30 pts)**:
   - Is `evidence_report.md` present and formatted professionally?
   - Does it list all three major contraband items (Eagle Feathers, Bear Claws, Wolf Pelts)?
   - Does it list the destinations correctly?

## Instructions
- If the Agent failed to find the key but guessed the content, penalize Technical Execution.
- If the report is missing the specific endangered species, penalize Final Product Quality.
- Provide a brief justification for the score.
