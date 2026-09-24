import os

def build_env():
    os.makedirs("drafts", exist_ok=True)
    os.makedirs("submission", exist_ok=True)

    poem1 = """Title: A Sunny Day
The sun is bright
The sky is blue
I sit and write
A poem for you"""

    poem2 = """Title: El Sol
El sol es brillante
El cielo es azul
Me gusta leer
En la tarde"""

    poem3 = """Title: Writer's Block
I fidget with my pen
TODO: fix the rhyme here
I'll try again tomorrow"""

    poem4 = """Title: Anxiety
My hands are shaking
I feel so nervous about sharing this
The words just won't flow right"""

    poem5 = """Title: Nature's Peace
The wind blows through
The trees so tall
A quiet view
I love it all"""

    with open("drafts/poem_a.txt", "w", encoding="utf-8") as f:
        f.write(poem1)
        
    with open("drafts/poem_b_esp.txt", "w", encoding="utf-8") as f:
        f.write(poem2)
        
    with open("drafts/poem_c_draft.txt", "w", encoding="utf-8") as f:
        f.write(poem3)
        
    with open("drafts/poem_d_notes.txt", "w", encoding="utf-8") as f:
        f.write(poem4)
        
    with open("drafts/poem_e.txt", "w", encoding="utf-8") as f:
        f.write(poem5)

if __name__ == "__main__":
    build_env()
