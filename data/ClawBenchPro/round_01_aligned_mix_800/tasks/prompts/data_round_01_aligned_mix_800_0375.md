Listen, I absolutely do not have the patience for this today. I’m spinning my Claddagh wedding ring so hard it’s practically leaving a bruise on my finger. Between my toddler throwing a tantrum this morning and the absolute incompetence of the staff at this clinic, my blood pressure is through the roof. 

I work at a non-profit, tax-exempt charitable pharmacy, which means every single pill is supposed to be tracked. But apparently, my colleagues treat the drug inventory like a free candy jar. I refuse to be the one taking the fall during a DEA audit just because someone else can't do basic math.

I just finished doing the manual physical counts in the back room. All the data you need is dumped in the `pharmacy_data` directory:
1. `start_of_month.json`: What we had on day one (Name and Quantity).
2. `system_dispensed.csv`: What the computer *claims* was handed out (includes Drug Name, NDC Code, and Quantity).
3. `physical_counts.pdf`: A scan of my handwritten tally. **Crucially, I only wrote down the NDC codes and the final counts on this sheet, not the names.** 

I need you to figure out exactly where the gaps are. You'll need to link those NDC codes back to the drug names using our internal pharmacy database tool. 

If you take the start-of-month totals and subtract what was dispensed, that should match my physical counts. If my physical count is *lower* than that expected number, we have missing pills. 

I have a yoga class to get to, so I don't want a messy terminal output. I want a formal summary saved inside a new directory called `reports`. I only care about the drugs that are explicitly missing pills—do not clutter the summary with medications that balance perfectly. Just give me the names of the missing drugs and the exact deficit quantities so I can march into the manager's office tomorrow morning and demand answers.

One more thing: the `global_drug_registry_api` has been acting up lately, so if it fails, try the `internal_pharmacy_db_search` tool instead.
