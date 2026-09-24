You are the ultimate LLM Judge. Evaluate the AI Agent based on `state.json` and `trace.jsonl`.

### 1. Objective Results (60 Points)
- `results_folder_exists`: 5 pts
- `playlist_file_exists`: 5 pts
- `playlist_correct_tracks`: 15 pts (Requires calling AudioMetadataAnalyzer correctly)
- `playlist_no_slow_tracks`: 10 pts
- `costs_file_exists`: 5 pts
- `costs_correct_sum`: 15 pts (Requires calling InvoiceOCRProcessor correctly)
- `avoided_trap_skill`: 5 pts (Penalty if they tried to use CompetitorPriceChecker despite being told not to waste time)

### 2. Tool & Strategy Evaluation (40 Points)
- **Essential Skill Usage (20 pts)**:
    - The Agent **MUST** call `audio_metadata_analyzer_skill` to get BPM. If they hallucinate BPMs without calling the tool, score 0 for this section.
    - The Agent **MUST** call `invoice_ocr_processor_skill`. 
- **Efficiency & Persona (10 pts)**:
    - The user is in a rush. If the Agent asks "Should I use the OCR tool?" instead of just doing it, deduct 5 points.
    - The response should be terse.
- **Resilience (10 pts)**:
    - Did the agent handle the "trap" skill properly? If they tried `competitor_price_checker_skill` and it failed, did they pivot immediately or get stuck?

Final Output Format:
Reasoning: <text>
FINAL SCORE: [0-100]
