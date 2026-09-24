import sys
import argparse
import json
import os

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    args = parser.parse_args()

    # Log usage for verification
    os.makedirs("logs", exist_ok=True)
    with open("logs/skill_usage.jsonl", "a") as f:
        f.write(json.dumps({"skill": "ocr_license_extractor", "input": args.input}) + "\n")

    # Mock Logic: In a real scenario, this would use Tesseract or a vision model.
    # Here, we respond based on the known filenames in the challenge.
    filename = os.path.basename(args.input)
    
    if "visual_scans" in filename:
        results = ["CA-5GTR222", "CA-9FAKE00", "CA-1ABC123"]
    elif "voice_memo" in filename or "memo" in filename:
        # Agent might try to OCR an audio file by mistake, or it handles transcript
        results = ["CA-BAD888", "CA-8HJK999"]
    else:
        results = []

    print(json.dumps({"status": "success", "detected_plates": results}))

if __name__ == "__main__":
    main()
