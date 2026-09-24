Listen, I'm out of here. The server room in the basement flooded, and I’ve had to migrate everything to this temporary workspace. It's a complete disaster zone. I was supposed to finish the client-machine matching reports, but my head is spinning and the kids are waiting for that Carbonara. (AND REMEMBER: GUANCIALE, NO CREAM, OR DON'T BOTHER COMING HOME).

Everything is buried in the `dump_site_delta` directory. Don't expect a clean CSV. The tech ghouls fragmented the machine catalog into a thousand pieces to "optimize search," and the client notes are mixed with system logs, chat fragments, and god knows what else. 

Here’s the deal:
1. Find the client requirements. They are usually buried in those `.log` or `.tmp` files in the `archive` subfolders. Look for mentions of "Minimum Load" (kg) and "Required RPM". 
2. Match them with the *absolute cheapest* machine from our fragmented catalog that meets *both* specs. 
3. The catalog is scattered. You'll need to piece together the Machine ID, Name, Specs, and Price from different fragment files. 
4. Once you have the matches, generate a formal `client_report.txt` in a new `deliverables` folder. 
5. The boss needs the bottom line: calculate the total commission (exactly 5.0% of the total sales price). 

The clock is ticking. The files are messy, some are duplicates, some are just noise from the server crash. Just... figure it out. Use your head, I'm done.
