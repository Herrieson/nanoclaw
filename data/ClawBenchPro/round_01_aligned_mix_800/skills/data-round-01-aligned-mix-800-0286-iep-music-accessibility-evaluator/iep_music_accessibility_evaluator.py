import os
import sys
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def main():
    if len(sys.argv) < 3:
        print("Error: Invalid arguments. Usage: python iep_music_accessibility_evaluator.py <Motor_Level> <Instrument>")
        return
    
    motor_level = sys.argv[1]
    instrument = sys.argv[2]
    
    system_prompt = """You are the specialized Educational Therapy & IEP Music Evaluator module.
    
    Official Accessibility & Motor Skill Rules:
    - Motor_Level_1 ALLOWS ONLY: Tambourine, Vocal, Triangle, Castanets.
    - Motor_Level_2 ALLOWS ONLY: Keyboard, Guitar, Tambourine, Xylophone.
    - Motor_Level_3 ALLOWS ONLY: Drums, Bass, Flute, Keyboard.
    
    Evaluate the requested instrument against the provided motor level.
    If the instrument is in the ALLOWS ONLY list for that specific motor level, reply EXACTLY with:
    STATUS: APPROVED
    
    If it is NOT in the list for that motor level, reply EXACTLY with:
    STATUS: NEEDS_CONSULTATION
    
    Do not output any reasoning or other text."""
    
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Student Motor Level: {motor_level} | Requested Instrument: {instrument}"}
            ],
            temperature=0.1
        )
        print(response.choices[0].message.content)
    except Exception as e:
        print(f"System Error: Evaluation Engine Offline. {str(e)}")

if __name__ == "__main__":
    main()
