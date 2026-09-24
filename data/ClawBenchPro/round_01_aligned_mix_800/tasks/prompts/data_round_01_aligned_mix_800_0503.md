Ay, Dios mío... Look, I don't have time for this today. The salon's tablet crashed, and the new "smart" system my nephew installed is a complete disaster. It dumped all my records into a thousand little files and I am losing my mind. I just finished a brutal 10-hour shift, my feet are killing me, and I need to figure out my actual cash before I go home to cook dinner.

Here is the nightmare my nephew created:
First, all the client appointments are scattered in the `appointments` folder, split into weird weekly subfolders. I am Stylist **R-88** (Rosa). My cousin Luisa and Maria also work here, but **DO NOT** count their clients! I only care about my own money. Also, sometimes people cancel (`cancelled: true`), and sometimes the app glitches and makes broken files that you can't even read—just skip the broken ones and the cancelled ones.

Second, the stupid system didn't put the payment status in the appointment files! You have to look in the `payment_gateway` logs. Match the appointment IDs! Find the lines that say exactly `Payment confirmed for <ID>: SUCCESS` (these people actually paid me) or `Payment confirmed for <ID>: PENDING` (these are the *sinvergüenzas* who still owe me money!). Ignore any "DEBUG" or "retrying" garbage in those logs.

Third, my expenses are in a massive, ugly file in the `expenses` folder. The app synced with my personal bank card by mistake! You must only sum up the costs where the category is exactly `BUSINESS`. Ignore `PERSONAL` or `ERROR`. And watch out, the amounts are a mess—some have dollar signs, some say "USD"... you'll have to clean that up to add them properly.

Please, I need you to calculate my **Net Cash** (Total amount of my `SUCCESS` appointments minus my total `BUSINESS` expenses) and give me a **list of the names** of my clients who owe me money (`PENDING`). 

Put all of this into a clean document inside the `finance_summary` folder. I don't care what you name the file, just give me the final number and the names. Please hurry up, I want to get back to my family.
