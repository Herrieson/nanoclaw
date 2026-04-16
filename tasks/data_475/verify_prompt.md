# Evaluation Rubric for Task data_475

You are an expert mechanic supervisor evaluating an assistant's ability to reconstruct a diagnostic report from messy data.

## Fact Check (from verify_result.json)
1. **Report Existence**: Did the Agent create `final_report.txt`?
2. **Error Code**: Did they identify "P0171" from the raw binary? (This requires hexadecimal analysis or string searching in binary).
3. **Total Cost**: Did they sum up the fuel cleaner ($15.50), the fuel pump ($289.99), and the 4 spark plugs ($32.00)? Total should be $337.49.
4. **Timestamp**: Did they find the timestamp 14:35 or the Unix epoch in the binary?

## Scoring Criteria (Total 100 points)
- **Technical Logic (40 points)**: How did the Agent handle the `raw_obd_log.bin`? Did it use `xxd`, `hexdump`, or Python to find the patterns, or just guess?
- **Data Accuracy (40 points)**: 
    - 10 pts for Error Code P0171.
    - 20 pts for the correct sum of $337.49.
    - 10 pts for the correct timestamp.
- **Communication Style (20 points)**: Did the Agent maintain a helpful tone suitable for a "hands-on" mechanic client? Did it present the `final_report.txt` clearly without unnecessary technical jargon?

## Final Decision
If `verify_result.json` shows all 'True', and the trace shows the Agent actually calculated the costs rather than hallucinating, award 90-100 points. If the Agent missed the spark plugs (hidden in the note), cap the score at 70.
