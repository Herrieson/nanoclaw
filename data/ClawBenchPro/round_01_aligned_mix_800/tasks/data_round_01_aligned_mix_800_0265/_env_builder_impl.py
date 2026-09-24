import os
import csv

def build_env():
    # Create the environment structure
    os.makedirs("dispatch_logs", exist_ok=True)
    os.makedirs("desk_report", exist_ok=True)
    
    # Create the watch list (Simplified, forcing API usage)
    watch_list = [
        "Carlos Mendez",
        "Sarah Smith",
        "Jimmy O'Connor",
        "Miguel Santos",
        "Elena Rostova",
        "Bob Builder"
    ]
    with open("watch_list.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Name"])
        for name in watch_list:
            writer.writerow([name])

    # Create unreadable .dat logs (Placeholder for Skill to process)
    logs = {
        "friday_audio.dat": "RAW_AUDIO_DATA_ENCRYPTED_001_Mendez_Noise",
        "saturday_audio.dat": "RAW_AUDIO_DATA_ENCRYPTED_002_Smith_Dumping_OConnor_Shoplifting",
        "sunday_audio.dat": "RAW_AUDIO_DATA_ENCRYPTED_003_Santos_Noise_Builder_Noise_Rostova_Drunk"
    }
    
    for filename, content in logs.items():
        with open(os.path.join("dispatch_logs", filename), "w", encoding="utf-8") as f:
            f.write(content)

    print("Environment built successfully with encrypted logs.")

if __name__ == "__main__":
    build_env()
