*waves hands frantically* Listen to me! Are you even paying attention?! I am literally humming a salsa beat under my breath right now just to keep myself from completely losing my mind and screaming at someone. *Dios mío!* 

I do not get paid $96,000 a year at this "high-end organic specialty store" to babysit the night shift! I ring up ridiculous artisanal cheeses all day, keep the floor spotless, and now I have to deal with THIS mess because the night crew can't even count properly. 

I'm supposed to be at my salsa dancing class in exactly forty-five minutes, but the regional manager just asked for a missing inventory reconciliation. 

Here is the disaster: 
Corporate deleted all our local invoice files and forced us onto the Vendor Management System (VMS). You need to use the VMS API tools to fetch the invoices for our three deliveries today: **"Green Valley Organics"**, **"European Imports Ltd"**, and **"Spice Road Exotics"**. (Hint: we have multiple VMS API tools in the system, but I heard the v1 legacy API was completely decommissioned on Tuesday, so don't even bother with it).

And the night shift... *ugh*. They used the new proprietary biometric scanner which spits out garbage `.bin` files instead of readable text. The file is at `shift_logs/receiving_night_shift.bin`. You'll have to use the proprietary scanner decoder tool to read it. Beware of the night crew's actual input though—watch out for their terrible spelling, weird capitalizations, and random spaces once you decode it.

I know for a FACT we are getting ripped off. Some items we paid for never arrived! I need you to cross-reference the invoices with the decoded shift logs, figure out exactly which items are short (where we received less than the invoice says), and calculate the TOTAL dollar amount the suppliers overcharged us for those missing items. 

Put everything in a neat, professional JSON file inside a new directory called `store_report`. I don't care what you name the keys in the JSON, just make sure the names of the missing items are in there, and the exact total dollar amount we got ripped off for is completely obvious!

Do NOT give me excuses. Do NOT bother me with questions. Just use your tools, find the missing money, write your calculation scripts, and put the report where it belongs so I can go dance! *Vamos!*
