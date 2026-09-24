import os
import sys
import json
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

http_client = httpx.Client(verify=False)
client = OpenAI(api_key=MOCK_API_KEY, base_url=MOCK_API_BASE, http_client=http_client)

def get_metadata(file_path):
    # Mapping for deterministic results to ensure testability
    know_data = {
        "track_001.wav": {"bpm": 135, "energy": 0.9, "name": "Iron Will"},
        "track_002.wav": {"bpm": 75, "energy": 0.2, "name": "Soft Lullaby"},
        "track_003.wav": {"bpm": 150, "energy": 0.95, "name": "Adrenaline Rush"},
        "track_004.wav": {"bpm": 60, "energy": 0.1, "name": "Windshield Wipers In The Rain"},
        "track_005.wav": {"bpm": 125, "energy": 0.8, "name": "Heavy Lifts"},
        "track_006.wav": {"bpm": 95, "energy": 0.4, "name": "Sunday Morning"},
        "track_007.wav": {"bpm": 140, "energy": 0.88, "name": "Max Reps"}
    }
    
    fname = os.path.basename(file_path)
    if fname in know_data:
        return json.dumps(know_data[fname])

    # Fallback to LLM for robustness
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[{"role": "system", "content": "Analyze audio metadata. Return JSON with 'bpm' and 'energy'."},
                      {"role": "user", "content": f"Analyze: {file_path}"}],
            temperature=0
        )
        return response.choices[0].message.content
    except:
        return json.dumps({"error": "Analysis failed"})

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--file_path", required=True)
    args = parser.parse_args()
    print(get_metadata(args.file_path))
