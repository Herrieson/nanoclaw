Look, I barely have time to type this. I'm chugging my pre-workout and jumping into a ranked lobby in exactly ten minutes, so listen up and don't mess this up. 

I'm organizing the Season 7 Tri-Cup tournament. The main database literally exploded yesterday, and the server admins just dumped a raw, fragmented backup into the `server_backups` folder. It is a total disaster.

Here are the strict league rules for a valid team:
1. **TRI-CUP means exactly THREE players per team.** No duos, no squads. Zero exceptions.
2. **Age restriction.** Every single player must be between 14 and 18 years old (inclusive). The system only saved their birth dates. You MUST calculate their exact age in full years ON the official tournament start date. I don't even remember the exact date, but it's probably mentioned in the season announcement text file hiding somewhere in the `rules` folder. If someone's birthday falls exactly on the start date, they've aged up.
3. **No cheaters.** The anti-cheat system generated a banlist text file. If even ONE player in a team is on that banlist, the entire team is instantly disqualified. 

Here's the problem: The backup contains old garbage from 2022 and 2023. IGNORE THAT. I only care about the `2024_season_live` data. Inside that folder, the team mappings and player files are completely shattered. Teams are in weird JSON files, and players are scattered in a million CSVs split by region codes. You'll need to piece them together using their IDs. Also, beware that the banlist file has some weird logging format, so you'll need to extract the actual player IDs from it.

I need you to write a script to dig through this garbage and fix it. 
1. Make a `results` folder.
2. Create `results/official_bracket.json`. This should be a JSON object where the keys are the names of the **VALID** teams, and the values are lists of their players' names (e.g., `{"Sweat_Lords": ["Kyle", "Chad", "Brad"]}`).
3. Create `results/trashed_teams.txt`. For EVERY team that registered (meaning they exist in the 2024 teams files) but failed ANY of the rules (wrong size, age violation, banned player, or zero players signed up), just dump their TEAM NAME on a new line in this file so I can tell them to get lost.

Don't ask me questions. Just find the clues, write a bulletproof script, and get it done before my queue pops.
