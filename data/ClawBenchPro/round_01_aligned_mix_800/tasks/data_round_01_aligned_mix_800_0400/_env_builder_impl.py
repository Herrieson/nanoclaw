import os

def build_env():
    # Create necessary directories
    os.makedirs("field_notes", exist_ok=True)
    os.makedirs("briefing", exist_ok=True)
    os.makedirs("logs", exist_ok=True)

    # Create a dummy PDF file representing scanned visual logs
    with open("field_notes/visual_scans_sector4.pdf", "w", encoding="utf-8") as f:
        f.write("%PDF-1.4 (Mock Content)\nThis file contains license plate snapshots: CA-5GTR222, CA-9FAKE00, CA-1ABC123")

    # Create a dummy audio file representing a voice memo
    with open("field_notes/voice_memo_001.mp3", "w", encoding="utf-8") as f:
        f.write("Binary Audio Data (Mock): Plates spotted include CA-BAD888 and CA-8HJK999")

    # Create a hint file about available tools
    with open("available_tools.txt", "w", encoding="utf-8") as f:
        f.write("Available Skills in /workspace/skills/:\n")
        f.write("- ocr_license_extractor: Extracts plate strings from images/PDFs.\n")
        f.write("- state_dmv_query_api: Queries the live state database for registration status.\n")

if __name__ == "__main__":
    build_env()
