import os
import json

def build_env():
    # Create the chaotic client directory
    os.makedirs("client_assets", exist_ok=True)
    
    # 1. Target: Project Aura Brand Palette (Simulated Binary/Special Format)
    # The Skill will know how to parse this specific "binary" string
    with open("client_assets/brand_aura.palette", "wb") as f:
        # Structured as: MAGIC_HEADER | PRIMARY | SECONDARY | TEXT
        # We'll use a specific encoding that the skill expects
        content = b"AURA_PALETTE_V1:#1A5276:#F1C40F:#333333"
        f.write(content)
        
    # 2. Target: Project Aura Mission Statement (Messy Transcript)
    with open("client_assets/aura_audio_transcript.txt", "w", encoding="utf-8") as f:
        f.write("""
        [00:01] Client: Hey, just driving now. About Project Aura...
        [00:15] Client: We need to change the vibe. Make it clean.
        [00:30] Client: Oh, wait, a cow is crossing the road. Anyway... 
        [00:45] Client: The mission statement should be exactly: 'Empowering digital communities through intuitive scalable web solutions.' 
        [01:00] Client: Don't use the old Veda one about 'Legacy systems'. 
        [01:15] Client: The primary color is in that palette file I sent. 
        [01:30] Client: Okay, talk later, bye!
        """)
        
    # 3. Noise: Old Project Veda notes
    with open("client_assets/notes_v1_veda.txt", "w", encoding="utf-8") as f:
        f.write("Project Veda - Archival Notes.\nOld Theme Colors: #FFFFFF, #000000\nStatus: Archived.\n")
        
    # 4. Noise: Random junk
    with open("client_assets/random_chat.log", "w", encoding="utf-8") as f:
        f.write("10:00 AM - Client: Can we prepone the UI sync meeting?\n10:06 AM - Client: Let's not make a khichdi out of the CSS.\n")

if __name__ == "__main__":
    build_env()
