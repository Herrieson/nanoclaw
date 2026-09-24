import os
import csv

def build_env():
    # Ensure we are creating things in the current working directory, 
    # which the framework guarantees is already the sandbox root.
    os.makedirs("dispatch_logs", exist_ok=True)
    
    # Create the watch list
    with open("watch_list.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "Prior_Offenses", "Last_Known_Address"])
        writer.writerow(["Carlos Mendez", "3", "142 Elm St"])
        writer.writerow(["Sarah Smith", "5", "River Rd Encampment"])
        writer.writerow(["Jimmy O'Connor", "2", "888 Oak Ave"])
        writer.writerow(["Miguel Santos", "1", "774 Pine Ln"])
        writer.writerow(["Elena Rostova", "4", "Unknown"])

    # Create messy dispatch logs with targets and distractors
    with open("dispatch_logs/friday_shift.txt", "w", encoding="utf-8") as f:
        f.write(">>> DISPATCH LOG - FRIDAY <<<\n")
        f.write("20:00 - Dispatch 104. Noise complaint at Elm St. Subject identified as Carlos Mendez. Issued formal warning to turn down the music.\n")
        f.write("22:30 - Dispatch 108. Public intoxication incident. Subject: Elena Rostova. Detained overnight in holding cell 3.\n")
        f.write("23:15 - Dispatch 110. Welfare check. No issues found.\n")

    with open("dispatch_logs/saturday_shift.txt", "w", encoding="utf-8") as f:
        f.write(">>> DISPATCH LOG - SATURDAY <<<\n")
        f.write("09:15 - Dispatch 201. Illegal dumping reported near the river basin. Witness got the license plate. Suspect confirmed as Sarah Smith. Fled scene.\n")
        f.write("14:20 - Dispatch 215. Shoplifting at the corner bodega. Subject: Jimmy O'Connor. Stole $40 worth of goods.\n")
        f.write("23:45 - Dispatch 240. Noise complaint. Loud party keeping neighbors up. Subject: Bob Builder. Not a known offender.\n")

    with open("dispatch_logs/sunday_shift.txt", "w", encoding="utf-8") as f:
        f.write(">>> DISPATCH LOG - SUNDAY <<<\n")
        f.write("02:10 - Dispatch 305. Noise complaint. Subject: Miguel Santos. Played loud bass heavy music. Refused to open door initially.\n")
        f.write("10:00 - Dispatch 312. Vandalism and graffiti on the overpass. Unknown suspect, but leaving a sketch pad behind.\n")
        f.write("15:30 - Dispatch 320. Traffic stop. Broken taillight. Warning issued.\n")

if __name__ == "__main__":
    build_env()
