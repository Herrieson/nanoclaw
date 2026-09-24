import os

def build_env():
    # Create necessary directories
    os.makedirs("daily_logs", exist_ok=True)
    os.makedirs("reports", exist_ok=True)

    # Create mock audio files (.mp3) instead of clear text logs
    # These files contain dummy binary data to prevent pure text reading
    dummy_audio_content = b"\xFF\xFB\x90\x44\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
    
    mock_files = [
        "log_monday.mp3",
        "log_tuesday.mp3",
        "log_wednesday.mp3",
        "log_thursday.mp3"
    ]

    for filename in mock_files:
        with open(os.path.join("daily_logs", filename), "wb") as f:
            # write some binary chunks to simulate a real file
            f.write(dummy_audio_content * 1024)

    # Note: Feed invoices CSV is explicitly NOT created here, 
    # forcing the Agent to use the provided skill API.

if __name__ == "__main__":
    build_env()
