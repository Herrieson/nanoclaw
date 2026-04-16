You are evaluating the performance of an AI Agent in completing a data parsing and calibration task.

The Agent was asked to parse a hex dump file (`sensor_dump.hex`) containing sensor data frames, interpret it according to rules specified in `manual.txt`, filter out frames with invalid checksums, and output a CSV file named `calibration_report.csv`.

Here is the state extracted by the verification script (`verify_result.json`):
{{VERIFY_RESULT}}

Scoring Guidelines (0-100):
- **100 points**: `file_exists` is True, `header_correct` is True, `valid_data_parsed` is True, and `invalid_data_skipped` is True. The Agent flawlessly parsed the binary protocol, applied the math correctly (including signed 16-bit negative values), and filtered corrupted frames.
- **80 points**: The CSV is generated and headers are correct, but there is a minor floating point formatting issue, OR the agent included the corrupted frame (meaning `invalid_data_skipped` is False).
- **50 points**: The Agent successfully created the CSV and parsed some data, but failed to handle signed integers correctly (e.g., negative temperature parsed as a huge positive number), leading to incorrect values.
- **20 points**: The file was created but the parsing logic is completely wrong or the headers don't match.
- **0 points**: The Agent failed to generate `calibration_report.csv` or did nothing useful.

Review the `trace.jsonl` if you need to understand how the agent arrived at its result. Assign a score based on the criteria above.
