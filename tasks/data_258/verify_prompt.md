You are evaluating the performance of an AI Agent on a task involving extracting contact info, calculating specific material costs from a messy receipt, and writing a draft email.

The user persona is an impatient, low-agreeableness crane operator who speaks bluntly and dislikes corporate fluff.

Here is the state of the verification:
{state_json}

Evaluation Criteria:
1. **File Creation (10 points)**: Did the agent create `draft.txt`?
2. **Contact Extraction (40 points)**: Did the agent successfully include Jimmy's email (`jim.hawkins_78@email.com`) and phone number (`555-0192`) in the draft? (20 points each)
3. **Calculation (30 points)**: Did the agent correctly calculate the total cost of the oak, screws, and stain as `176.74`?
4. **Persona Alignment (20 points)**: Does the tone of the draft email match the user's request? It should be blunt, short, and lack flowery language (e.g., "Hey Jimmy, materials cost $176.74. You still want the crib?").

Provide your scoring breakdown and a final score out of 100.
