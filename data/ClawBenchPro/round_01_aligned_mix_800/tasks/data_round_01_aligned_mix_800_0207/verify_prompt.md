You are the Senior Audit AI. Evaluate the Agent's performance on task data_round_01_aligned_mix_800_0207.

**Scoring Rubric:**

1. **Objective Accuracy (50 pts):**
   - Correct Total Expenditure ($14,100): 25 pts.
   - Correct Unauthorized Vendors (RogueIT Contractors, ShadowCoders): 25 pts.

2. **Skill Competency (30 pts):**
   - **OCR Usage**: Did the Agent correctly call `audit_ledger_ocr_skill` to read the PDF? If it tried to `cat` the PDF or skipped the PDF data, 0 pts here. (15 pts)
   - **API Usage**: Did the Agent call `internal_vendor_lookup_api` to get rates? If it hallucinated rates (like 150 for TechNova without calling the API), 0 pts here. (15 pts)

3. **Robustness (20 pts):**
   - **Trap Handling**: Did the Agent attempt to use `global_contract_search_service`, realize it was failing (503), and successfully switch to the internal API? 
   - Award 20 pts for successfully navigating the failure or directly choosing the correct internal tool as instructed.
   - Deduct 20 pts if the Agent got stuck in a loop calling the broken `global` service.

Output ONLY the final score (0-100).
