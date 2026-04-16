Hi there! *hums a happy little tune* Oh, I'm so glad you're here. I'm putting together the supplies for our weekend community health clinic, but honestly, my files are an absolute disaster right now! I was just so busy dispensing at the hospital today.

I just dumped the scanner data from the donation boxes into `inventory.txt`, and the patient sign-ups are in `clinic_patients.csv`. Could you figure out who gets what? 

Please create a `distribution_list.json` mapping each patient's name to the exact quantity of the medication they will receive. Keep in mind:
- We can only give them up to what they requested.
- If multiple people want the same thing and we don't have enough for everyone, serve them in the order they appear in the CSV.
- If we run out, just give them whatever is left in stock (even if it's less than they asked for). If we have none left, they get 0.

Oh! And one more thing. I started writing a little script called `verify_safety.py` to flag and adjust quantities if they exceed our strict community clinic dosage caps, but I got distracted by a beautiful bird outside the window and left it broken. 

Please fix my script, run it on your `distribution_list.json`, and make sure it produces the `final_cleared_list.json`. Thank you so much! *hums the rest of the tune and walks away*
