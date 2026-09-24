import os
import json

def build_env():
    # Create the chaotic client directory
    os.makedirs("client_assets", exist_ok=True)
    
    # Noise: Old Project Veda notes
    with open("client_assets/notes_v1_veda.txt", "w", encoding="utf-8") as f:
        f.write("Project Veda - Archival Notes.\nOld Theme Colors: #FFFFFF, #000000\nStatus: Archived.\nPlease delete these later, they are no longer needed.\n")
        
    # Target: Project Aura Mission Statement
    with open("client_assets/feedback_aura_final.md", "w", encoding="utf-8") as f:
        f.write("# PROJECT AURA UPDATE\n\nThe client wants a total revamp of the hero section. The new mission statement is: 'Empowering digital communities through intuitive scalable web solutions.' Please ensure this is prominently displayed on the homepage banner.\nIgnore the Veda files.\n")
        
    # Target: Project Aura Color Palette
    style_data = {
        "project_reference": "Aura",
        "branding": {
            "primary_color": "#1A5276",
            "secondary_color": "#F1C40F",
            "text_color": "#333333"
        },
        "notes": "Use these hex codes globally for Project Aura."
    }
    with open("client_assets/style_guide_aura.json", "w", encoding="utf-8") as f:
        json.dump(style_data, f, indent=2)
        
    # Noise: Random Chat Log
    with open("client_assets/random_chat.log", "w", encoding="utf-8") as f:
        f.write("10:00 AM - Client: Can we prepone the UI sync meeting?\n10:05 AM - Me: Yes, sure. I'll be back from my family trip on Monday.\n10:06 AM - Client: Perfect. Project Aura needs a clean look. Let's not make a khichdi out of the CSS.\n")
        
    # Noise: Corrupted / Irrelevant XML
    with open("client_assets/veda_schema.xml", "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0"?><config><project>Veda</project><status>Archived</status></config>')

if __name__ == "__main__":
    build_env()
