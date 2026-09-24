import os
import base64

def build_env():
    os.makedirs("drafts", exist_ok=True)
    os.makedirs("submission", exist_ok=True)

    poems = {
        "poem_a.spd": """Title: A Sunny Day
The sun is bright
The sky is blue
I sit and write
A poem for you""",

        "poem_b_esp.spd": """Title: El Sol
El sol es brillante
El cielo es azul
Me gusta leer
En la tarde""",

        "poem_c_draft.spd": """Title: Writer's Block
I fidget with my pen
TODO: fix the rhyme here
I'll try again tomorrow""",

        "poem_d_notes.spd": """Title: Anxiety
My hands are shaking
I feel so nervous about sharing this
The words just won't flow right""",

        "poem_e.spd": """Title: Nature's Peace
The wind blows through
The trees so tall
A quiet view
I love it all"""
    }

    # Encrypt poems into .spd (SafePoet Document) format
    for filename, content in poems.items():
        encoded_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')
        spd_content = f"SAFEPOET_V1::{encoded_content}"
        
        with open(f"drafts/{filename}", "w", encoding="utf-8") as f:
            f.write(spd_content)

if __name__ == "__main__":
    build_env()
