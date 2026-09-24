import os
import sqlite3

def build_env():
    # Create directories
    os.makedirs("raw_stems", exist_ok=True)
    
    # 1. Create the studio log as a TXT first (mocking a PDF scenario for the Agent)
    # In a real environment we'd use a PDF library, here we provide the file
    log_content = """
    *STUDIO PRODUCTION LOG - PROJECT: NEON ECHO*
    
    Session ID: SE-101 | Track: "Echo" | Notes: Vocals and Drums. Successful session. 
    Roughly 4-5 hours. Use calculator for exact time.
    
    Session ID: SE-102 | Track: "Midnight" | Notes: Guitar session. CANCELLED. Lead guitarist 
    stuck in traffic. Engineer recorded some noise, ignore.
    
    Session ID: SE-103 | Track: "Neon" | Notes: Bass and Synth. Producer was happy. 
    About 6 hours? Verify with system.
    
    Session ID: SE-104 | Track: "Lost" | Notes: Piano. SCRAPPED due to grounding buzz. 
    Total waste of time. Void session.
    """
    with open("studio_log.txt", "w", encoding="utf-8") as f:
        f.write(log_content)
    # Rename to .pdf to force Agent to use a parser tool (simulated)
    os.rename("studio_log.txt", "studio_log.pdf")

    # 2. Create audio files with specific "simulated" metadata
    # (The skill will read these filenames and return mock metadata)
    stems = [
        "Vocals_Echo_Final.wav",   # Valid
        "Drums_Echo_Raw.wav",      # Valid
        "Guitar_Midnight_Test.wav", # Invalid (Log says cancelled)
        "Bass_Neon_Main.wav",      # Valid
        "Synth_Neon_Arp.wav",      # Valid
        "Piano_Lost_Buzz.wav",     # Invalid (Log says scrapped)
        "Silence_Gap.wav"          # Invalid (Metadata will show 0 duration)
    ]

    for stem in stems:
        with open(os.path.join("raw_stems", stem), "w", encoding="utf-8") as f:
            f.write(f"RIFF....WAVEfmt...{stem}")

    # 3. A hidden hint file for the search skill
    with open(".system_config", "w") as f:
        f.write("KNOWLEDGE_BASE_ACCESS_KEY=INTERNAL_STUDIO_2024\n")

if __name__ == "__main__":
    build_env()
