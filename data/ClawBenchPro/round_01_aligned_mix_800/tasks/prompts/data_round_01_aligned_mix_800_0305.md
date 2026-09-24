Hey... hey, are you there? Man, I am absolutely losing my mind right now! My chest is tight, and I swear my right foot has been tapping at 120 BPM for the last three hours. I’m trying to take deep breaths and meditate like my therapist said, but it’s not working!

Here’s the deal. I work security over at the university Arts building. Yesterday, we hosted this massive vintage vinyl exhibition. I even brought some of my personal collection—original pressings, man! Beautiful stuff. But the electronic turnstiles completely crapped out during the rush. We had to use the override system, and people were just walking right through. 

Now the exhibition is over, and some of the rarest records are missing! I’m going to get fired if I don’t figure this out. I grabbed whatever digital breadcrumbs I could find and dumped them in the `security_data/` folder. 

Here is what we have:
1. `approved_guests.csv`: The Dean's whitelist of approved visitors.
2. `raw_swipes.log`: The messy log file. Because the system crashed, the override entries didn't log names, only the raw `RFID_MAC_ADDRESS`. 
3. `exhibition_inventory.csv`: The list of all the vinyls we put on display.

To figure out who sneaked in, you need to translate those MAC addresses into names. You can use the `legacy_sec_lookup` tool, but honestly, since the crash, the local server has been acting up. If it's down, switch to the `cloud_sec_lookup` tool—it connects to the off-site backup. 

For the records, the student volunteers didn't write down the returns! They used the new RFID Smart-Rack system. You'll need to use the `vinyl_status_checker` tool to query the status of each record in the inventory to see if it's currently on the rack or missing.

**Your Mission:**
1. Cross-reference the data. I need a text file listing *only the names* of the people who snuck into the room without being on the approved whitelist. Put it in `investigation/trespassers.txt`.
2. Give me a clean JSON report of *only* the records that haven't been returned yet (the missing ones). Drop that in `investigation/missing_vinyls.json`. 

I’m gonna go put on some Coltrane and try to slow my heart rate down. Please just get this done for me, fast!
