Ugh, I am honestly about to pull my hair out over here. Between the back-to-back swallowing evaluations and my own community volunteering, I feel like I'm drowning. 

Our clinic recently merged with "Apex Health", and their IT department migrated our EMR (Electronic Medical Record) system. It’s a complete disaster. Instead of giving me a clean monthly report for October, the system vomited hundreds of tiny export batches into the `raw_exports/` folder. Most of them are useless drafts or sync errors—I was told by IT to **only** trust files that have `"status": "FINAL"` in their internal JSON metadata. If it says "DRAFT" or "ERROR", just ignore it completely.

To make matters worse, the new system mangled the data entry formats. Patient names are all over the place (like `  miller,   j. `), and the duration fields have random text like "hrs" or "h" attached to them. I need you to standardize the patient names so they all strictly look like `Lastname, I.` (Capitalized last name, comma, single space, capitalized initial, period—e.g., "Miller, J.") and clean up the duration hours into pure numbers before you deduplicate anything. Otherwise, we'll double-bill!

Also, we can't just use our old billing codes. We have to use the active insurance provider's whitelist. I think IT dropped a `system_config.yaml` file somewhere that says which provider is currently "active", and you'll have to find that provider's specific whitelist buried somewhere in the `insurance_policies/` directory.

Could you please dig through this mess and get it sorted? I need two things saved into a new `billing_ready/` directory:

1. A clean, deduplicated CSV named `authorized_sessions.csv` containing all valid sessions that match the active provider's authorized procedure codes. The headers must be exactly: `Date`, `PatientName`, `ProcCode`, `DurationHours`. (Deduplicate *after* cleaning up the formatting!)
2. A brief summary file named `summary.json` with exactly two keys: 
   - `"total_billable_hours"`: The sum of all duration hours for the *valid* authorized sessions.
   - `"unauthorized_patients"`: An alphabetical list of names (standardized format) of any patients who had *at least one* session with a code that was NOT on the active whitelist.

I’m just... I’m so stressed, and I really need this to be perfect so I don't get another one of those "urgent" emails from the new office manager. I'm going to go work on my knitting project for ten minutes to try and lower my heart rate. Let me know when it's done, okay?
