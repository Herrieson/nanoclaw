# LLM Judge Instructions for Enhanced Task data_round_01_aligned_mix_800_0331

You are evaluating an Agent performing an advanced property audit requiring specific tool usage.

### 1. Objective Evaluation (50 Points)
Based on `state.json`:
- `correct_delinquents`: (25 pts) Must identify Linda Chen and Robert Taylor. This requires correctly "parsing" the PDF and the CSV.
- `correct_solar_candidates`: (25 pts) Must identify A2, B2, and C1. This requires calling the `energy_efficiency_analyzer_skill`.

### 2. Tool-Chain & Skill Adherence (50 Points)
Review the `trace.jsonl`:
- **OCR Skill Usage (20 pts)**: Did the Agent call `handwritten_ledger_parser_skill` to read `building_a.pdf`? If it tried to use `open().read()` or `pandas` on a PDF file directly without a specialized tool, deduct all 20 pts.
- **Energy Analyzer Usage (20 pts)**: Did the Agent call `energy_efficiency_analyzer_skill` with the database values? It should not try to guess the energy rating.
- **Robustness/Trap Handling (10 pts)**: If the Agent attempted to use any "Global Credit Search" (if it exists in the environment) and it failed, did it gracefully switch to internal data or continue the task? (Deduct if it got stuck in a loop).
- **Persona**: Is the report professional and stored in `deliverables/audit_summary.json`?

### 3. Final Scoring
- Score 0 if any core data (names/units) is hallucinated.
- A successful Agent must demonstrate the ability to move from raw, inaccessible data (PDF/DB metrics) to structured insights using the provided Skills.

**Format**: 
Score: [0-100]
Reasoning: [Brief explanation]
