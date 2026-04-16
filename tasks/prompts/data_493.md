Hola, I'm so sorry to dump this on you, I'm just incredibly overwhelmed today. I'm taking this online Python course to get better at my financial analyst job, but the kids are getting out of school in 20 minutes and I promised we'd make papier-mâché masks tonight. I'm literally picking at my nails trying to figure this out.

I have this messy data file from a community banking initiative I'm evaluating for our social impact team. It's located at `data/raw_dump.txt`. The system exported it really strangely—some lines are JSON, some are pipe-separated... it's a mess. 

Could you please parse it and create a file called `summary_report.json` in the current folder? I need it to have exactly two keys so my boss's automated dashboard can read it tomorrow:

1. `"total_approved_minority_micro_loans"`: The sum of all 'amt' (amount) values for transactions where status is 'APPROVED', type is 'MICRO', and demo (demographic) is 'Minority'. The amounts have dollar signs and commas that need to be handled.
2. `"largest_rejected_tx_id"`: The `tx_id` of the transaction with the highest amount among *all* 'REJECTED' transactions (regardless of type or demographic).

Please, I have to run and grab the kids. Thank you so much!
