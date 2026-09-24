It’s been a long day. The feds raided the offshore servers before our insider could download a clean, consolidated database. Instead of a neat little spreadsheet, I’ve just been handed a massive, fragmented data dump, and the clock is ticking.

Our intel team has compiled a profile of the syndicate ringleaders in `intel/target_profiles.json`. Be careful—some of these guys have been neutralized or went dark. I only care about the targets marked with an `ACTIVE` status. 

We don't have their banking account numbers, only their street aliases. You'll have to dig through the raw identity dumps in the `sys_dumps/account_registry/` directory to figure out which account IDs belong to our active aliases. It's a mess of random files in there.

As for the money trail, the transaction logs are scattered across dozens of regional nodes in the `server_nodes/` directory. The bank’s backend is completely schizophrenic: some nodes export logs as CSVs, others as JSONs, and the system admins clearly couldn't agree on column headers or key names. 

A few things to watch out for:
1. They operate internationally. The transaction amounts are in various currencies, but I need the final totals strictly in USD. I managed to scrape their internal conversion table—you'll find it at `exchange_rates.json`. 
2. The ledgers include failed transfers, bounced checks, and pending holds. Obviously, the suspects only get rich off transactions where the status is explicitly `COMPLETED` or `SUCCESS`. Ignore the rest.

I need you to write a script to sift through this nightmare. Map the active aliases to their total successfully acquired funds in USD. Round each final total to exactly 2 decimal places. 

Create a new directory named `dossier` and save your findings in `dossier/master_totals.json`. The JSON should use the *Aliases* as keys and the calculated totals as values. No excuses, no partial work. Get it done before my briefing at dawn.
