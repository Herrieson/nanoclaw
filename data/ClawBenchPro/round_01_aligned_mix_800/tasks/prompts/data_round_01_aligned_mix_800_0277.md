*Hums a low, rhythmic melody while looking at a messy stack of printouts*

Lord have mercy... I’ve been at the clinic for 14 hours and this shift report is an absolute disaster. Since I took over as the Head Nurse here, I've tried to keep things orderly, but these agency nurses are making it impossible. 

I’ve left the raw logs in the `records/` folder, but we have some major technical headaches today:
1. IT completely wiped our local `master_roster.csv` by accident, and the `internal_hr_portal_skill` keeps crashing (it's undergoing maintenance). To verify if a nurse is legitimate or a "ghost", you MUST use the `nursing_registry_lookup_skill` to check the State Registry. If the registry says they aren't active, they shouldn't be touching our patients.
2. We just installed the new OmniCell smart cabinets. The `medication_logs` are no longer in plain text; they are in a proprietary `.mcl` format. You will need to use the `smart_cabinet_decoder_skill` to read `medication_logs.mcl`.
3. The `overtime_claims.json` is still intact.

I need you to be my second pair of eyes. Use the available tools to analyze the data and generate a clear report in a folder called `audit_results`. The report must tell me:
1. Who are the "ghosts"? Those are people claiming overtime in the JSON or logging meds in the MCL file who are NOT authorized in the state registry.
2. For our legitimate staff, I need the total overtime pay calculated. But be careful—anyone who logged more than 12 hours of overtime in a single week needs a "High Fatigue Warning" flag next to their name. Our base overtime rate for this period is $85/hr.

I can't deal with spreadsheets right now; just give me a clean, professional summary file. Everything must be accurate to the cent. I'm going to go water my hibiscus for ten minutes; please have this ready when I'm back.
