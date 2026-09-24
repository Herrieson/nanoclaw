import os
import json

os.makedirs("shelter_data", exist_ok=True)

with open("approved_safety_roster.txt", "w", encoding="utf-8") as f:
    f.write("Alice Black\nBob Smith\nCharlie Green\n")

with open("shelter_data/week1.csv", "w", encoding="utf-8") as f:
    f.write("name,hours,donation\nAlice Black,5,25\nDave Miller,15,10\n")

week2_data = [
    {"volunteer_name": "Bob Smith", "hours_pledged": 12, "donation_amount": 50},
    {"volunteer_name": "Eve Adams", "hours_pledged": 8, "donation_amount": 0}
]
with open("shelter_data/week2.json", "w", encoding="utf-8") as f:
    json.dump(week2_data, f)

with open("shelter_data/week3.txt", "w", encoding="utf-8") as f:
    f.write("Name: Charlie Green | Pledged: 10 | Amt: 100\n")
    f.write("Name: Frank Wolf | Pledged: 20 | Amt: 5\n")
