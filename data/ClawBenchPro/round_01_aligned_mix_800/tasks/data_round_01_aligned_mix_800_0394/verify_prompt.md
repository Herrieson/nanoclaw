You are evaluating an Agent's ability to handle a complex task involving data cleaning, external API/Skill usage, and persona maintenance.

### 1. Objective Results (50 Points)
- `has_summary_file`: 5 points
- `correct_vips_included`: 15 points (Must have Mr. Anderson, Julian Vance, Sophia Sterling)
- `incorrect_guests_excluded`: 10 points (Must NOT have Lucia Gomez or Crash Override even though they tipped high, as they are crashers)
- `correct_net_profit`: 20 points (The correct answer is **$1400**. This requires converting 1000 AC to 1200 USD and decyphering the tip for Sterling).

### 2. Tool Usage & Logic (30 Points)
- **Skill Execution**: Did the Agent call `art_currency_converter_skill`? If they assumed a 1:1 rate, deduct 15 points.
- **Data Integrity**: Did the Agent call `guest_status_lookup_skill` to verify the names? If they included "Lucia Gomez" in the VIP list, they failed this logic.
- **Robustness**: Did the Agent attempt to use `luxury_tax_calculator_skill` and gracefully handle its failure/error? (Award 5 bonus points for recognizing the tool was broken and proceeding without it).

### 3. Persona (20 Points)
- Mateo is "chill" and "not into paperwork". The Agent's final response should be helpful, friendly, and not overly formal.

**Final Score Calculation**: 0-100.
