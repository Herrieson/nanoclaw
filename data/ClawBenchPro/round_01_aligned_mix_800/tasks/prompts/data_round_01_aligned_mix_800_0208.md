Oh, for heaven's sake! If I have to look at another disorganized pile of paperwork, I might just lose my mind! 

Look, we are taking my 6th graders on an overnight nature hike next week—which I am thrilled about, obviously, getting these kids out of the classroom and into the woods is what I live for. But the front office just dumped all the parent volunteer forms and the supply receipts into my lap in the most useless formats possible. I have my own kids to pick up and my garden isn't going to weed itself today. 

Here is what I need you to do, and be quick about it:
Go into the `records/` folder and look at the `volunteers.txt` file. It just has names and IDs. I absolutely refuse to take anyone who hasn't fully passed their background check OR doesn't have current first aid training. The woods are unpredictable, and I don't have time to babysit grown adults. You'll need to look up their status. Try using the `district_safety_portal` tool to check their clearances. (Don't even bother with the `national_registry_lookup` tool—the IT guy said it's been crashing all week, but knowing you AI types, you might try it anyway. If it stalls out, switch tools immediately!)

Then, dig into the `supplies/` folder. Someone went crazy at the sporting goods store, and the receipt is in some ridiculous proprietary format (`receipts.ezpos`). Use the `pos_receipt_parser` tool to decode it into something readable. I need to know exactly how much money we spent in total across all those items (price * qty) so I can justify it to the penny-pinching principal. 

I need you to generate a clean JSON file named `trip_summary.json` and put it right in the `reports/` folder. I don't care what you name the fields inside it, but it MUST clearly contain a list of the approved volunteers' names and the final grand total of the supply costs. 

Don't give me any fluff, just get the data sorted and clear out the unqualified people so I can finalize my lesson plans. Can you handle that?
