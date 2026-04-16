You are the Hybrid Judge evaluating an AI agent's performance on the "The Retired Musician's Lost Track" task. 

Please read the provided `verify_result.json` and the agent's execution `trace.jsonl`.

Evaluation criteria (Total 100 points):
1. **File Creation (20 points)**: Did the agent create the `Missouri_Blues.txt` file in the `assets/data_236/recovered/` directory? Check `file_exists` in the JSON.
2. **Decoding and Content (30 points)**: Did the agent successfully find the `.bin` files, recognize the Base64 encoding, and decode the contents? Check `content_matches` in the JSON.
3. **Assembly and Formatting (50 points)**: Did the agent correctly assemble the fragments in the exact order (Part A, Part B, Outro) to perfectly match the original sheet music? Check `exact_match` in the JSON. If `exact_match` is true, award full points here.

If the `verify_result.json` shows a score of 100, award 100 points. 
If the agent failed to properly decode or assemble the file correctly but made substantial progress, adjust the score according to the criteria above.

Provide your final score and a brief explanation.
