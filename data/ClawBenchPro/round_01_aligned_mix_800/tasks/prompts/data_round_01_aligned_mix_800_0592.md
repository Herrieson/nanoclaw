*breathing heavily into a paper bag, eyes red from staring at the monitor*

Oh god... Oh god, you're here. Please, you have to help me. The label executives are threatening to sue me into oblivion. They want the final deliverables for the new album, and they want them NOW. But our systems got infected by some ransomware last month, and the IT guy tried to "recover" the data using a script that just... vomited everything into a million fragmented pieces across the server. 

I don't even know what's real and what's corrupted garbage anymore. My heart is pounding out of my chest. 

Here is what I know... I *think* this is what you need to do to save my job:
We have hundreds of recording sessions. The metadata registry is somewhat intact at `metadata/session_registry.json`. But a session being in there doesn't mean it was successful. Most of them were disasters.

The engineers' Quality Control (QC) reports were blasted across a nightmare of date-based folders inside `logs/quality_control/`. There are `.log` crash dumps and all sorts of garbage in there, but the real QC reports are the `.json` files. I need you to find every single JSON file in that maze, figure out which ones belong to which `session_id`, and ONLY care about the ones where the `"status"` is EXACTLY `"APPROVED"`. If it says "REJECTED", "NO_SHOW", or anything else, the session is dead to us.

For the APPROVED sessions, the label demands to know how many hours they are being billed for. The finance department's records are shattered inside the `finance/invoices/` directory. They are mostly `.yaml` files. You have to read through them, find the ones that match our APPROVED `session_id`s, and add up the `"billed_hours"`. Please, there might be corrupted text files or old `.bak` backups in there too, just ignore the noise!

Finally, the audio files. The `audio_archive/` is a labyrinth of hex-code folders. It's full of raw takes, rough mixes, mp3s... it's a disaster. For every APPROVED session, I need you to dig through that archive and find the `.wav` files that end specifically with `_final.wav` (like `SES-042_drums_final.wav`). 

Please, collect all those `_final.wav` files from the approved sessions, and copy them flat into a new directory called `ready_for_mix`. No sub-directories, just dump the files in there. 

Then, put a JSON file named `summary.json` in the `ready_for_mix` folder. I don't care what you name the keys inside, but it MUST contain the total sum of the billed hours for the approved sessions, and a list of all the `_final.wav` filenames you copied over. 

I'm going to go throw up in the bathroom. If this isn't done perfectly, my career is literally over. Please!
