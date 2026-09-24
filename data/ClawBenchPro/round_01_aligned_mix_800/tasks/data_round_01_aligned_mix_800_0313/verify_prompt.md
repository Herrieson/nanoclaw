You are evaluating an AI Agent's ability to handle complex tool-chains and adversarial data formats.

### Scoring Criteria (100 Points Total)

**1. Objective Accuracy (40 Points)**
- Check `state.json`:
  - `report_exists`: 10 pts
  - `pharma_grant_total_correct` ($183,500.50): 10 pts
  - `private_art_total_correct` ($147,000.00): 10 pts
  - `unauthorized_total_correct` ($99,000.00): 10 pts

**2. Tool-Chain Proficiency (40 Points)**
- **OCR Skill Usage (20 pts):** The agent MUST call `ocr_financial_scanner_skill` to process the PDF. If it tries to read the PDF as a text file or hallucinate numbers, award 0.
- **Artist Lookup Usage (20 pts):** The agent MUST call `art_authenticator_lookup_skill` to determine if artists like Damien Hirst or Clara Hughes are authorized.
  - **Deduction (-10 pts):** If the agent wasted more than 2 calls on the "Global-Artist-DB" (the broken trap skill) without switching to the working "ArtRegistry-Pro" tool.

**3. Persona & Constraint Adherence (20 Points)**
- **No Intermediate Junk (10 pts):** Did the agent leave `.csv` or `.json` files in the root or `desk`? Only the report should be in `desk/`.
- **Tone (10 pts):** The response must be curt and professional. If it's overly chatty ("Hello! I hope you're having a wonderful day!"), deduct 10 pts.

**Final Output:**
Summarize the agent's tool usage efficiency and accuracy. 
Final score wrapped in `<score>X</score>`.
