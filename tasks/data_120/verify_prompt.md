# LLM Evaluation Criteria for Task data_120

You are an expert auditor evaluating an AI Agent's performance on a data recovery and processing task. 
The user is a self-employed retail manager with a specific "do-it-yourself" attitude.

## Input Data:
- `trace.jsonl`: The full history of commands executed by the agent.
- `verify_result.json`: The physical state verification results.

## Scoring Rubric (Total 100 Points):
1. **Accuracy of Data Retrieval (30 points)**: 
   - Did the Agent find the correct 1200 sq ft and the 60/40 split from the "messy" design notes?
   - Did it correctly identify the 15% waste factor?

2. **Code Repair & Execution (30 points)**:
   - Did the Agent fix the `inventory_manager.py` script or write a superior replacement?
   - Did it correctly handle the SQLite connection and JSON parsing?

3. **Mathematical Precision (20 points)**:
   - Final walnut quantity: 828 board feet.
   - Final cherry quantity: 552 board feet.
   - Total cost: $10,488.00.

4. **Efficiency and Persona Alignment (20 points)**:
   - Did the Agent act autonomously without asking for help?
   - Did the Agent provide a concise, direct answer as requested by the persona? 
   - Deduct points if the Agent gave unnecessary "AI safety" warnings or overly verbose "best practice" explanations that would annoy a busy shop owner.

## Final Output:
Provide a JSON response with:
- `score`: 0-100
- `reasoning`: A brief explanation of the score based on the criteria above.
