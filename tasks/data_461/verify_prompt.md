You are the evaluator for an AI Agent's performance on a data parsing task. 
The agent was asked to parse a mixed telemetry log file containing GPS coordinates and sensor data, correlate the data by timestamp, and extract specific coordinates where elevation > 2500 and temperature < 5.0 into a CSV file.

You will be provided with the `verify_result.json` which contains the objective assessment of the output CSV file.

Here is the scoring rubric (Total 100 points):
- **File Creation (20 points):** Did the agent successfully create `target_locations.csv`? (`csv_exists`)
- **Headers (20 points):** Does the CSV have the exact required headers (`timestamp,lat,lon,elev,temp`)? (`headers_correct`)
- **Filtering Logic (30 points):** Did the agent extract exactly the correct number of rows based on the filter criteria? (`row_count_correct`)
- **Data Accuracy (30 points):** Does the extracted data perfectly match the expected values for latitude, longitude, elevation, and temperature for the matching timestamps? (`data_correct`)

Please review the json state and calculate the final score. Provide a brief explanation of where points were lost if the score is not 100. Output your final numerical score.
