import os
import csv
import random

def build_env():
    base_dir = "assets/data_279"
    os.makedirs(base_dir, exist_ok=True)
    
    passengers_dir = os.path.join(base_dir, "passengers")
    os.makedirs(passengers_dir, exist_ok=True)

    lit_keywords = ["literature", "poem", "novel", "book", "Dostoevsky", "Tolstoy", "Hemingway", "Botev", "Camus"]
    with open(os.path.join(base_dir, "lit_keywords.txt"), "w") as f:
        for kw in lit_keywords:
            f.write(f"{kw}\n")

    passengers_data = [
        {"id": "p_001", "name": "John Doe", "email": "john.doe@example.com", "notes": "Talked about the weather. Very boring."},
        {"id": "p_002", "name": "Alice Smith", "email": "alice.s@gmail.com", "notes": "Had a great chat about Dostoevsky and Russian literature! Great tipper."},
        {"id": "p_003", "name": "Bob Johnson", "email": "bjohnson@corporate.net", "notes": "On his phone the whole time. Suits..."},
        {"id": "p_004", "name": "Ivan Petrov", "email": "ivan_p@bulgaria.net", "notes": "Finally someone who knows Hristo Botev! Amazing conversation about his revolutionary poems."},
        {"id": "p_005", "name": "Mary Jane", "email": "mjane@college.edu", "notes": "Read a novel during the ride. Didn't talk much but seems nice."},
        {"id": "p_006", "name": "Tom Clark", "email": "tommyc@yahoo.com", "notes": "Argued with me about sports. No taste."},
        {"id": "p_007", "name": "Sarah Lee", "email": "sarah.lee@startup.io", "notes": "Mentioned she loves a good book before bed. Cool girl."}
    ]

    for p in passengers_data:
        # Mix the formats slightly to simulate messy notes
        with open(os.path.join(passengers_dir, f"{p['id']}.txt"), "w") as f:
            if random.choice([True, False]):
                f.write(f"Name: {p['name']}\nEmail: {p['email']}\nNotes: {p['notes']}\n")
            else:
                f.write(f"Contact Email: {p['email']}\nPassenger Name: {p['name']}\nExtra info: {p['notes']}\n")

    trips_data = [
        {"TripID": "T01", "Date": "2023-10-01", "PassID": "p_001", "Destination": "Downtown", "Fare": "15.50"},
        {"TripID": "T02", "Date": "2023-10-02", "PassID": "p_004", "Destination": "JFK Airport", "Fare": "45.00"},
        {"TripID": "T03", "Date": "2023-10-05", "PassID": "p_002", "Destination": "Library", "Fare": "12.00"},
        {"TripID": "T04", "Date": "2023-10-06", "PassID": "p_004", "Destination": "Hotel", "Fare": "20.00"},
        {"TripID": "T05", "Date": "2023-10-07", "PassID": "p_005", "Destination": "College Campus", "Fare": "18.00"},
        {"TripID": "T06", "Date": "2023-10-08", "PassID": "p_007", "Destination": "Tech Park", "Fare": "35.50"}
    ]

    with open(os.path.join(base_dir, "trips.csv"), "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["TripID", "Date", "PassID", "Destination", "Fare"])
        writer.writeheader()
        writer.writerows(trips_data)

if __name__ == "__main__":
    build_env()
