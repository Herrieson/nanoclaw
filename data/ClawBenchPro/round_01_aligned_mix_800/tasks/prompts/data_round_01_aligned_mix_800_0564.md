Look, I'm at my breaking point. It's midnight, the heating in this office is dead, and the file server just had a partial stroke. I need to file a motion by 8 AM, or we lose the 'Smith v. State' leverage.

Everything is a mess in the `archive_recovery` folder. My paralegal, Miller, was supposedly "helping" but I suspect he was running rogue sessions. I need a definitive `audit_report.json` in the `final_drop` folder.

Here’s the deal:
1. **The Schedule**: There are multiple "Master Schedules" in the `scheduling_backups` folder. Look at the file headers or metadata; only the one marked as the "Final Verified Version" in its internal notes is the source of truth.
2. **The Logs**: The `raw_transcripts` directory is a nightmare—hundreds of fragments. Some are just auto-save garbage, some are actual logs. Real deposition logs always contain a "Session-ID" and a "Verification-Stamp". 
3. **The Audit**:
    - **Missing Sessions**: Scheduled events that have no corresponding verified transcript.
    - **Ghost Sessions**: Transcripts that exist but aren't on the official schedule.
    - **The Miller Incident**: I heard Miller was taking statements in 'Smith v. State' sessions. He’s a paralegal, not an attorney. If "Miller" appears as the "Lead_Interrogator" in any 'Smith v. State' transcript, I need that flagged specifically.

I don't have time to walk you through the directory tree. The filenames are messy—some use YYYY-MM-DD, some use Julian dates, some are just hex strings. You'll have to look *inside* the files. Just give me the JSON categorized by `missing_depositions`, `unscheduled_depositions`, and `unauthorized_appearances`. Move.
