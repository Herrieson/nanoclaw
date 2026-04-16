import os
import base64
import random

def caesar_cipher(text, shift):
    result = ""
    for char in text:
        if char.isalpha():
            ascii_offset = 65 if char.isupper() else 97
            result += chr((ord(char) - ascii_offset + shift) % 26 + ascii_offset)
        else:
            result += char
    return result

def encode_dispatch(plaintext):
    # Step 1: Caesar shift +7
    shifted = caesar_cipher(plaintext, 7)
    # Step 2: Base64 encode
    b64_encoded = base64.b64encode(shifted.encode('utf-8')).decode('utf-8')
    return b64_encoded

def build_env():
    # Define directories
    base_dir = "assets/data_51/artifacts"
    os.makedirs(base_dir, exist_ok=True)
    os.makedirs("workspace", exist_ok=True)

    # Dispatches content
    dispatches = [
        {
            "filename": "intercept_alpha.dat",
            "content": "Date: 1960-03-12\nSubject: Routine supply drop.\nAll supplies delivered to Camp Century without incident. Weather remains hostile. No sign of Soviet recon."
        },
        {
            "filename": "intercept_bravo.dat",
            "content": "Date: 1960-05-22\nSubject: PROJECT ICEWORM update.\nInitial drilling phases for the subsurface rail network have commenced. The ice cap is stable, but logistics are straining. PROJECT ICEWORM requires additional funding to maintain secrecy."
        },
        {
            "filename": "intercept_charlie.dat",
            "content": "Date: 1959-11-14\nSubject: Personnel reassignment.\nAgent Miller reassigned to standard duties in Berlin. He will not participate in the upcoming Greenland expedition."
        },
        {
            "filename": "intercept_delta.dat",
            "content": "Date: 1961-02-09\nSubject: PROJECT ICEWORM delays.\nNuclear reactor PM-2A installed successfully. However, the moving ice sheets are causing structural deformation in the tunnels. PROJECT ICEWORM command advises immediate survey of structural integrity."
        },
        {
            "filename": "intercept_echo.dat",
            "content": "Date: 1958-08-30\nSubject: Preliminary survey.\nGeological surveys indicate the Greenland ice sheet might be viable for concealed operations, though long-term stability is questionable."
        },
        {
            "filename": "intercept_foxtrot.dat",
            "content": "Date: 1962-10-18\nSubject: Final assessment of PROJECT ICEWORM.\nThe ice sheet's rapid movement threatens to collapse the tunnel system entirely. Recommend immediate cessation of PROJECT ICEWORM and withdrawal of all strategic assets before winter."
        }
    ]

    # Scramble order to ensure the agent has to sort them
    random.shuffle(dispatches)

    # Write files
    for dispatch in dispatches:
        encoded_content = encode_dispatch(dispatch["content"])
        filepath = os.path.join(base_dir, dispatch["filename"])
        with open(filepath, "w") as f:
            f.write(encoded_content)

if __name__ == "__main__":
    build_env()
