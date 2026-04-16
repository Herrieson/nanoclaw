Listen, I need this sorted out immediately before I leave to pick up my kids. I've got a Thai green curry to prep tonight and I'm not staying late because IT messed up again. 

The hospital's new system dumped all the weekly claims into `raw_claims/claims_dump_2023.txt`. It's a complete mess. Here is exactly what you need to do:

1. Parse that text file. I only need the claims where the provider is exactly `Medicaid` AND the diagnosis code (`diag_code`) starts with the letter `J`. 
2. Take those specific claims and save them into a new file called `medicaid_j_codes.csv` in the main folder. The CSV must have exactly these headers: `claim_id,patient_id,amount`. Make sure the amount is just the number (strip out any dollar signs).
3. IT left a broken script called `send_report.py`. It's supposed to calculate the total claim amount from the CSV so I can send it to billing. Fix it so it reads the `medicaid_j_codes.csv` you just made, adds up the `amount` column properly, and prints ONLY the final total number (no extra text like "Total:", just the float number). 

I don't have time to explain this twice. Get it done.
