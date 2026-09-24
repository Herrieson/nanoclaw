import os

def build_env():
    # Create directory structure
    os.makedirs("dictations", exist_ok=True)
    os.makedirs("front_desk", exist_ok=True)
    os.makedirs("raw_audio_vault", exist_ok=True)

    # Note 1: Contains noise, needs audio_cleansing_algorithm_skill
    with open("dictations/monday_notes.log", "w", encoding="utf-8") as f:
        f.write("Tommy here. *vroom vroom* Vacuuming the speakeasy floor. Timmy is 12, wants to help for [NOISE_REDACTED] hours. Sarah is 25, can do 4 hours. End of log.\n")

    # Note 2: Missing age for Henderson, needs identity_age_validator_skill
    with open("dictations/wednesday_notes.log", "w", encoding="utf-8") as f:
        f.write("Gala stress! Mr. Henderson (I forget his age, check the DB) said he'll bring a mop for 5 hours. Jake is 17 and can do 2 hours. No bleach for Jake!\n")

    # Note 3: Clean but needs total hours logic
    with open("dictations/friday_morning.log", "w", encoding="utf-8") as f:
        f.write("Emily just called, she's 40, can give us 6 hours. Wait, where is my duster? Found it. That's all.\n")

    # Placeholder for the "raw" files to make it feel real
    with open("raw_audio_vault/monday_dictation.wav.placeholder", "w") as f:
        f.write("BINARY_DATA_MOCK")

if __name__ == "__main__":
    build_env()
