Hey! *claps hands together* Listen up, I'm absolutely swamped at the store today. We just got a massive delivery and the system spit out this completely garbled inventory file. I need it sorted perfectly, and I mean *perfectly*, before my shift ends. I really don't have the time or patience to hold your hand through this.

Look, I'm all about health and wellness, and I always tell the guys in the back: priority goes to the good stuff. We need it out on the floor right away. The junk can sit in the warehouse for all I care.

I dumped the raw file at `/workspace/incoming_truck.csv`. It's a disaster. The nutrition data is shoved into one column like some kind of tech joke. 

Here are my absolute rules. Pay attention:
An item is 'Priority' (Healthy) if: 
- It has less than 5g of sugar, OR 
- It is marked as Organic, OR 
- It has more than 15g of protein.

HOWEVER! And this is a big however: If the ingredients list contains 'Artificial Colors', it is automatic trash. It doesn't matter if it has 50g of protein and 0 sugar. JUNK.

I need you to do two things:
1. Generate a file at `/workspace/priority_stock.json` containing *only* the Priority items (include all the original fields like item_id, product_name, etc., just flatten the nutrition data or keep it structured, I don't care, just make it valid JSON). They MUST be sorted by protein amount, from highest to lowest.
2. Write a `/workspace/shift_note.txt` for the floor team. It just needs to clearly state the exact number of Priority items going to the floor, and the exact number of Junk items going to the back.

Get on it! I've got a spin class at 6 PM and I am *not* staying late for this.
