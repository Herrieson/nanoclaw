Look, I am absolutely losing my mind here! *throws hands up* The absolute GARBAGE property management software we use just imploded, and my boss is breathing down my neck. On top of that, I have to host my book club in exactly two hours—we're discussing *Wuthering Heights*, which is incredibly fitting right now because I feel like I'm wandering the moors going completely insane!

I need you to fix the accounting ledger IMMEDIATELY. The raw transaction logs are dumped in the `raw_logs` folder, and the current messed-up ledger is `ledger.csv`. 

Here is what I know: the system was supposed to calculate the total paid by each tenant. BUT, the incompetent developers somehow programmed it to count 'PENDING' transactions TWICE for Oakwood Apartments, and it totally ignored Maple Ridge! Honestly, I don't trust a single number in that file anymore.

Your job: Parse all those log files. Calculate the ACTUAL total paid for each tenant across all properties. ONLY 'SUCCESS' status transactions should be counted! Discard anything 'FAILED' or 'PENDING'.

Output a new file called `corrected_ledger.csv` with exactly three columns: `Property,Tenant,True_Total_Paid`. Then write a `summary.txt` telling me which tenants were over-reported and which were under-reported in the original ledger. 

Do not mess this up. I do not have the time or the patience to hold your hand through this!
