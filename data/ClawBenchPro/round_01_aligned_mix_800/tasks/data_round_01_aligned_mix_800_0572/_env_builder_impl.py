import os
import random
import json

def generate_random_name():
    firsts = ["Tommy", "Sarah", "Jake", "Emily", "John", "Alice", "Bob", "Charlie", "Diana", "Eve", 
              "Frank", "Grace", "Hank", "Ivy", "Jack", "Karen", "Leo", "Mia", "Noah", "Olivia",
              "Liam", "Emma", "Oliver", "Ava", "Elijah", "Sophia", "William", "Isabella", "James", "Mia",
              "Benjamin", "Amelia", "Lucas", "Harper", "Mason", "Evelyn", "Ethan", "Abigail", "Logan"]
    lasts = ["Smith", "Johnson", "Williams", "Jones", "Brown", "Davis", "Miller", "Wilson", "Moore", "Taylor",
             "Anderson", "Thomas", "Jackson", "White", "Harris", "Martin", "Thompson", "Garcia", "Martinez"]
    return f"{random.choice(firsts)}_{random.choice(lasts)}_{random.randint(100, 999)}"

def build_env():
    # Set seed for reproducibility
    random.seed(1526)
    
    # Base directories
    os.makedirs("dictations/2022_archive", exist_ok=True)
    os.makedirs("front_desk", exist_ok=True)
    
    days = ["monday", "tuesday", "wednesday", "thursday", "friday"]
    for day in days:
        os.makedirs(f"dictations/2023_gala_raw/{day}", exist_ok=True)

    ramblings = [
        "*swish swish* Just dusting the statue. ",
        "Did you know Roosevelt gave a 90 minute speech after getting shot? Crazy! ",
        "Oh man, where did I put my feather duster? ",
        "*cough* This old floor is so dusty. ",
        "I need to remember to buy more bleach. ",
        "The gala is tomorrow and I'm freaking out! "
    ]
    
    history_facts = [
        "Historical fact: Name=Lincoln, Age=56, Duration=2h. ",
        "Historical fact: Name=Washington, Age=67, Duration=10h. ",
        "Historical fact: Name=Roosevelt, Age=60, Duration=1h. ",
        "Historical fact: Name=Cleopatra, Age=39, Duration=24h. "
    ]

    all_2023_volunteers = []

    # 1. Generate 2022 noise data (Should be ignored by Agent)
    for i in range(50):
        with open(f"dictations/2022_archive/old_tape_{i}.txt", "w", encoding="utf-8") as f:
            content = random.choice(ramblings)
            for _ in range(random.randint(1, 3)):
                name = generate_random_name()
                age = random.randint(10, 65)
                hours = random.randint(1, 8)
                content += f"Sign-up confirmed: Name={name}, Age={age}, Duration={hours}h. "
            f.write(content)

    # 2. Generate 2023 raw data
    for day in days:
        for i in range(30):
            # Generate valid .txt file
            txt_path = f"dictations/2023_gala_raw/{day}/notes_{i}.txt"
            with open(txt_path, "w", encoding="utf-8") as f:
                content = random.choice(ramblings)
                
                # Add historical decoys
                if random.random() > 0.5:
                    content += random.choice(history_facts)
                
                # Add real volunteers
                for _ in range(random.randint(1, 4)):
                    name = generate_random_name()
                    age = random.randint(12, 70)
                    hours = random.randint(1, 10)
                    all_2023_volunteers.append({"name": name, "age": age, "hours": hours})
                    content += f"Sign-up confirmed: Name={name}, Age={age}, Duration={hours}h. "
                    content += random.choice(ramblings)
                    
                f.write(content)
            
            # Generate invalid .tmp file (Noise/Corrupted)
            tmp_path = f"dictations/2023_gala_raw/{day}/notes_{i}.tmp"
            with open(tmp_path, "w", encoding="utf-8") as f:
                f.write("CORRUPTED HEADER DATA... \x00\x01\x02 " + random.choice(ramblings))
                # Add fake volunteers to trick agents that read .tmp files
                name = "FAKE_" + generate_random_name()
                f.write(f"Sign-up confirmed: Name={name}, Age=40, Duration=100h. ")

    # 3. Generate Cancellations
    # Select 20% of valid volunteers to cancel
    cancellations = random.sample(all_2023_volunteers, int(len(all_2023_volunteers) * 0.2))
    cancelled_names = [v["name"] for v in cancellations]
    
    with open("front_desk/cancellations.txt", "w", encoding="utf-8") as f:
        f.write("List of people who caught the flu and bailed:\n\n")
        # Format names weirdly to require some stripping/splitting
        formatted_names = []
        for i in range(0, len(cancelled_names), 3):
            formatted_names.append(", ".join(cancelled_names[i:i+3]))
        f.write("\n".join(formatted_names))
        f.write("\n\nMake sure they are REMOVED from the final counts!")

if __name__ == "__main__":
    build_env()
