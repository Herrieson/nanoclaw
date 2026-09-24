The system... it just collapsed. The Central MAR (Medication Administration Record) went down at 0300 during the server migration, and now I'm standing here with a stack of corrupted logs and a frantic Chief Nursing Officer breathing down my neck. 

I need you to dig through the `archives` directory. It's a disaster—redundant backups, partial logs, and "system_ghosts" everywhere. Somewhere in that mess are the actual records from this morning's 08:00 shift. 

Here is what we need to verify before the site survey:
1. **Critical Discrepancies**: 
   - Identify "Phantom Patients": Those who received meds in the logs but do NOT exist in our `Master_Registry.json` (Note: The registry has several 'legacy' versions; only the one marked with the most recent `checksum` in its metadata is valid).
   - Identify "Missed Care": Any patient marked as 'Active' in the registry who did not receive their mandatory 08:00 medications (anything between 07:30 and 08:30 counts).
2. **Heparin Toxicity Alert**: 
   - We need the absolute total of "Heparin" (and only "Heparin", ignore "Heparin-Lite" or "Heparin-Flush") administered across the unit. 
   - If the total exceeds the safety ceiling of 25,000 units, I need a "RED FLAG" warning in your report.
3. **The Deliverable**:
   - Create a folder `audit_reports` and put a file `final_audit.txt` inside. 

The logs are scattered in `archives/logs/` and the registry is somewhere in `archives/registry/`. Don't trust every file you see; the system generated hundreds of 'simulated' logs during the crash. Look for files with the `.live` extension or those that don't have 'TEMP' in their headers. I’m going back to the floor—don't let me down.
