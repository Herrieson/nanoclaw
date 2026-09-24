Listen, I'm at my breaking point. The transition to the "Legacy-Bio" system has been an absolute catastrophe. The hospital servers are a graveyard of corrupted directories, and it seems the new residents have treated HIPAA regulations like a suggestion rather than the law.

I've been trying to run a compliance audit on the cardiology and neurology intake logs, but the data is hemorrhaging everywhere. These interns have been leaking Patient SSNs (XXX-XX-XXXX) directly into the `notes` or `comment` fields across hundreds of fragmented files. I tried to organize them into the `archives/raw_intake/` directory, but the server glitched—now everything is buried in a mess of nested subdirectories, mixed formats, and a sea of "recovery" decoys.

You need to find the truth in this wreckage. I need a JSON audit report saved to `vault/compliance_final.json`. It must map each **valid Doctor ID** to the **total number of SSN violations** they are responsible for. 

A few warnings from someone who's been staring at this screen for 20 hours:
1. Only count violations from the **Active Personnel**. There's a `staff_manifest.json` hidden somewhere in the `metadata` tree that defines who is currently active. Ignore any logs from "Retired" or "Terminated" staff.
2. The logs are a mess. Some are JSON fragments, some are pipe-delimited TXTs, some are CSVs. The field names aren't consistent either—look for things like 'public_note', 'entry', or 'patient_remark'.
3. Watch out for the `_backup_` and `_temp_` files. They contain duplicate or simulated data that will skew your counts. Only process files that follow our current naming convention (hint: the manifest might mention the valid log prefix).
4. If an SSN is redacted (like XXX-XX-1234), it's NOT a violation. Only the full, reckless exposure of the standard 3-2-4 digit format counts.

I don't care how you do it, just get me the numbers. If this isn't perfect, the board will have my head.
