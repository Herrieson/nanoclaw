Hey... so I kinda messed up really bad and I am literally freaking out right now. haha... 

I'm holding my favorite copy of *Pride & Prejudice* just trying to remember to breathe. Basically, I dropped out of college a few months ago, I'm sitting on like $60,000 in student loan debt, and I've been selling off my rare book collection to make rent. I'm usually SUPER organized about this, but I was trying to write a script to handle my orders and I completely corrupted my main database. 

I have to ship these orders out tomorrow morning or I'm going to get reported for fraud, and I can't afford to deal with that. I managed to scrape together my raw server logs (`server_logs.txt`), my customer address list (`shipping_addresses.csv`), and my original bookstore pricing catalog (`book_catalog.json`). 

In the logs, there are lines where the system recorded an order being placed. It usually looks like a mess of debug info, but the buyer's ID and the book's ISBN are in there somewhere. 

I need you to build a file called `shipping_manifest.json` in this folder for me. It needs to be a valid JSON array containing an object for every single order found in the logs. Every object MUST have exactly these keys:
- `buyer_name` (from the csv)
- `address` (from the csv)
- `isbn` (from the logs)
- `book_title` (from the catalog)
- `final_price` (this is a number, not a string. I ran a strict 15% off sale on ALL books to clear them out, so it should be exactly 85% of the original catalog price, rounded to 2 decimal places).

Please please please help me piece this back together. I know all the files are right here in the workspace. I'm going to go make some tea to calm my nerves. Thank you!!
