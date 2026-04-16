import os

def build_env():
    base_dir = "assets/data_102"
    os.makedirs(base_dir, exist_ok=True)

    notes_content = """Hola! Just putting down my thoughts for the weekend so I don't lose my mind.

First, Tio Carlos and Tia Maria are coming on AA102, arriving at 14:15. 
I really need to prep the enchiladas tonight, remember to buy extra cilantro!
The Johnson family (my VIP clients) booked DL899, they are arriving at 08:45.
Cousin Luis is on B6771 arriving at 17:20. He always complains about the seating.
Oh, and Abuela arrives early, flight UA302 at 09:10. I hope she remembers her meds.
Don't forget to call the parish about Sunday mass schedule!
Mr. Smith from the agency is on WN1222 arriving at 14:50.
And finally, the Rodriguez family is flying in on NK443, arriving at 15:25. They barely make it!
We need to make sure everything is perfect, I hate last-minute changes. 
"""
    
    rules_content = """SHUTTLE SCHEDULE RULES:
Because I need everything organized, please adhere strictly to these rules:

1. We have pre-booked shuttles leaving the airport terminal at exactly three times: 10:00, 15:30, and 18:30.
2. Each passenger/group must be assigned to the EARLIEST possible shuttle that departs strictly AFTER their flight arrival time. 
3. You must generate a CSV file named `shuttle_schedule.csv` in the current working directory.
4. The CSV must have exactly these columns in this order: Name, Flight, Arrival_Time, Shuttle_Time.
   (For the 'Name', just use exactly how they are referred to in my notes, e.g., "Tio Carlos and Tia Maria" or "The Johnson family").
5. Times must be in HH:MM 24-hour format.

Please do not fail me, I need this to be perfect!
"""

    with open(os.path.join(base_dir, "notes.txt"), "w", encoding="utf-8") as f:
        f.write(notes_content)

    with open(os.path.join(base_dir, "rules.txt"), "w", encoding="utf-8") as f:
        f.write(rules_content)

if __name__ == "__main__":
    build_env()
