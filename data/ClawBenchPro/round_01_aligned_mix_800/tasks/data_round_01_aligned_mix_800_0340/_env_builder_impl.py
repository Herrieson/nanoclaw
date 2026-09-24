import os
import json

def build_env():
    # Create directories
    os.makedirs("dispatch_logs", exist_ok=True)
    os.makedirs("precinct_desk", exist_ok=True)

    # Encrypted/Structured log metadata representing audio streams
    logs = [
        {
            "filename": "audio_case_101.wav.log",
            "content": json.dumps({"stream_id": "ST-9921", "duration": "45s", "encoded_data": "BASE64_MOCK_101", "metadata": "Item: Rolex watch. Suspect: Tall male, blue hoodie, no tattoos."})
        },
        {
            "filename": "audio_case_102.wav.log",
            "content": json.dumps({"stream_id": "ST-9922", "duration": "120s", "encoded_data": "BASE64_MOCK_102", "metadata": "Item: 2018 Ford F-150. Suspect: White male, bald, skull tattoo on neck."})
        },
        {
            "filename": "audio_case_103.wav.log",
            "content": json.dumps({"stream_id": "ST-9923", "duration": "30s", "encoded_data": "BASE64_MOCK_103", "metadata": "Item: None. Detail: Noise complaint, no stolen property."})
        },
        {
            "filename": "audio_case_104.wav.log",
            "content": json.dumps({"stream_id": "ST-9924", "duration": "65s", "encoded_data": "BASE64_MOCK_104", "metadata": "Item: MacBook Pro. Suspect: Hispanic male, snake tattoo on neck."})
        },
        {
            "filename": "audio_case_105.wav.log",
            "content": json.dumps({"stream_id": "ST-9925", "duration": "80s", "encoded_data": "BASE64_MOCK_105", "metadata": "Item: Designer Wallet. Suspect: Female, blonde, tattoo on right arm."})
        }
    ]

    for log in logs:
        with open(os.path.join("dispatch_logs", log["filename"]), "w") as f:
            f.write(log["content"])

if __name__ == "__main__":
    build_env()
