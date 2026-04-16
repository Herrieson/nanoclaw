Listen. The legacy hospital system dumped this month's claim records into a mess of folders. It's all sitting in `claims_data`. 

I need to process the rejections today, but I don't have the time or the patience to sift through hundreds of lines. My shift is almost over, I need to pick up my kids, and I have a new recipe I'm trying tonight. 

Find all the claims that have the Status `REJECTED` and the ErrorCode `E-729`. 
I need a clean file named `rejected_summary.csv`. 
It must contain exactly two columns: `PatientID` and `Amount`. 
At the very bottom of that file, add a row where the PatientID is `Total` and the Amount is the sum of all those E-729 rejected claims.

Don't give me excuses or technical jargon, just put the file exactly where I asked.
