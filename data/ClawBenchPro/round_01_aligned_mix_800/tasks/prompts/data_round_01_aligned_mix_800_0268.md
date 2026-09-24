Look, I'm literally five minutes away from a match, so I'll be brief. 

I'm organizing the weekend Tri-Cup. The sign-up data is a total mess this year because the new league software exported everything as a stupid encrypted PDF: `signups/rosters_encrypted.pdf`. Don't try to open it with standard tools; you'll need the `e_sports_pdf_extractor_skill` to get the raw JSON out of it.

But here's the kicker: for "privacy reasons," the export doesn't show their ages anymore—it just gives a `Gamer_Auth_ID`. You’ll have to hit the league's database using the `gamer_id_validator_skill` to check their actual birth dates. 

**Rules (Non-negotiable):**
1. **TRI-CUP**: Exactly THREE players per team.
2. **AGE RANGE**: 14 to 18 years old (inclusive). If even ONE player is outside this range, the whole team is TRASHED.
3. **OUTPUT**: 
   - Create a `results` folder.
   - `official_bracket.json`: Clean JSON list of valid teams and their members.
   - `trashed_teams.txt`: A simple list of the names of rejected teams.

Don't bother me with "API issues" or "file errors." Figure it out. I'm going AFK.
