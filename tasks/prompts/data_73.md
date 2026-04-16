Listen to me! The morons I manage at the pharmacy have messed up the inventory AGAIN! I swear, nobody wants to work hard anymore, and I have to clean up everyone's mess. I spent an hour just wiping down the counters today because someone left a smudge, and my back is absolutely killing me now. 

I come home to an empty house, my head is pounding, and my brain just feels completely foggy tonight. I cannot process these spreadsheets right now, but I need this sorted out immediately before my blood pressure spikes any higher.

Here is what you need to do. I have a system inventory file, an employee list, and a mess of audit logs in the `./` directory. I need you to cross-reference the expected inventory with the latest physical counts in the audit logs. 

Find EVERY single medication that has a MISSING quantity (where the latest physical count is less than the expected system inventory). I don't care about the ones that match. I only care about what's missing and who the last person to touch it was!

I need this organized PERFECTLY. You are to write the results to a file exactly at `missing_report.txt`. 
The format MUST BE EXACTLY this for each missing item:
`[ID] - [Medication] - Missing: [Number] - Last Handled By: [EmployeeName]`

Sort the lines in the file by the medication ID in ascending order! Do NOT add any extra blank lines, headers, or stupid pleasantries in the text file. I will lose my mind if the format is wrong. Just get it done.
