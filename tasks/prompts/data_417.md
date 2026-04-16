Yo bruh. So I was tinkering with this busted RFID scanner from the store, right? Manager let me take it home since they upgraded the system. I rigged it up to scan the crates of new kicks we got in the back room today. But the log it spit out is straight up garbage, like all hex and weird padding. No cap, I don't know how to read it fr. 

I dropped the log in `rfid_dump.txt` and a list of the upcoming hyped drops in `releases.json`. I need you to figure out how to decode that scanner dump, find the product codes (SKUs), and check 'em against the releases file. 

Find all the kicks we actually got in the scan that have a hype score strictly greater than 80, and drop their SKUs in a new file called `hyped_inventory.txt`. Just put one SKU on each line so I know exactly what to secure before my next shift. Good looking out!
