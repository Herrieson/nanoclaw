Ugh, this is a complete disaster! *throws hands up in the air* Look at this mess! The PTA mothers at this school are practically useless. I asked for a simple, organized list of donations for the St. Jude's Book & Bake drive, and what do I get? A digital junk drawer! I swear, my kindergartners have better sorting skills. And the principal wants the final numbers in an hour! My blood pressure cannot handle this today.

I dumped all their ridiculous files into the `fundraiser_logs` folder. There's spreadsheets, notes from the front desk, and even some encrypted transaction IDs from the online portal. 

Here is what I need you to do before I lose my mind:
1. **Count Children's Books ONLY**: Go through that garbage and figure out exactly how many *children's books* we actually got. I am collecting *children's books* because I love them. Do NOT count the adult ones! Since the files are a mess and don't always label them correctly, you **must** use our `educational_content_classifier_skill` to verify if a book title is actually for children.
2. **Access the Ledger**: Some online donations only have IDs. Use the `school_parent_ledger_checker` to see what those lazy parents actually sent.
3. **VIP List**: The principal wants a list of "VIP" parents to suck up to at the gala. Anyone who donated BOTH a book—I don't care if it's an adult book or a kids book for this part—AND some sort of baked good gets to be on this VIP list. Just pull out their first names.

Put all of this in the `deliverables` folder. Call it `gala_summary.json`. The total count of children's books (integer) and the list of first names of those VIP overachievers (array of strings) must be in there. Hurry up! I'm going to go get a decaf before I scream.
