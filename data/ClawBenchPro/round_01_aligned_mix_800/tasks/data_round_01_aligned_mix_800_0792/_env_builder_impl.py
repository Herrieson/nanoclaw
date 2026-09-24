import os

def build_env():
    # Create directories
    os.makedirs("raw_stems", exist_ok=True)
    
    # Create messy studio log
    log_content = """*Studio Production Log - Week 4*
Oh man, this week has been exhausting. 

Monday: We worked on the track "Echo". Recorded the vocal takes and the drum fills. It was a really smooth session, everyone was in a great mood. We billed for 4.5 hours.

Tuesday: Was supposed to be the "Midnight" guitar session. I booked the room for 3 hours, but the session was completely CANCELLED because the lead guitarist got stuck in traffic and went home. The engineer might have recorded some mic test files, but ignore them.

Wednesday: Focused on "Neon". We laid down the basslines and the synth arpeggios. The producer was a bit demanding, but we got it done. Took us exactly 6.0 hours.

Thursday: "Lost" piano session. We spent 2 hours trying to get a good take, but there was this horrible grounding buzz in the console. We had to scrap the whole thing. Consider this session cancelled and voided.
"""
    with open("studio_log.txt", "w", encoding="utf-8") as f:
        f.write(log_content)

    # Create dummy audio stems (Valid and Invalid)
    stems = [
        "Vocals_Echo.wav",
        "Drums_Echo.wav",
        "Guitar_Midnight.wav", # Invalid (Cancelled)
        "Bass_Neon.wav",
        "Synth_Neon.wav",
        "Piano_Lost.wav",      # Invalid (Scrapped)
        "Random_Noise_Test.wav" # Irrelevant
    ]

    for stem in stems:
        with open(os.path.join("raw_stems", stem), "w", encoding="utf-8") as f:
            f.write(f"Dummy audio data for {stem}\n")

if __name__ == "__main__":
    build_env()
