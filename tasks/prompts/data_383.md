Hey buddy. Listen, I'm out on the lake fishing and my phone is blowing up. 

The makeshift pump monitor I rigged up at the warehouse is spitting out alerts. I threw the logging scripts together real quick last weekend so they're a bit of a mess, formatting is all over the place. Everything is sitting in the `/workspace/pump_system/` folder. 

One of the pumps is failing—the pressure is tanking way below the normal 100 PSI mark. I need you to get in there and figure out which pump is acting up. Once you find it, calculate its average pressure from all its log entries today, and dump that exact number into a new file called `bad_pump_avg.txt` in that same folder so I can show the boss on Monday.

After that, go into the system config file in that folder. Shut down the bad pump and turn on its backup. I don't remember the exact wording I used for the JSON statuses, just improvise and make sure the bad one is marked offline or disabled, and its backup is active or online.

Appreciate it, partner. Let me get back to my fishing!
