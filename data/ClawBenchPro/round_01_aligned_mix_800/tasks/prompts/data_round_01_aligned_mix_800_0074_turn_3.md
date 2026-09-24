Audit day. *tap tap tap*. Corporate is breathing down my neck. I need this finalized before my church group meeting tonight.

My manager left some strict instructions in `docs/manager_notes.txt`, and the reinsurance company just sent over their absolute maximum limits in `audit/reinsurance_audit.csv`.

Here is what you must do: aggregate ALL the approved claims you processed across both batches. Group them by category. If the total approved amount in any category exceeds the limit specified in the reinsurance audit file, we have a massive problem. To fix it, you must proportionally scale down *every single claim* in that specific category so that the sum of the approved amounts exactly equals the reinsurance limit for that category. Round the final adjusted amounts to 2 decimal places. If a category is under the limit, leave those claims exactly as they were.

Generate the final, adjusted master list of all claims across both batches at `processed/final_adjustments.csv` with the headers `ClaimID,Category,FinalAmount`. I am trusting your meticulousness on this. Do not let me down.
