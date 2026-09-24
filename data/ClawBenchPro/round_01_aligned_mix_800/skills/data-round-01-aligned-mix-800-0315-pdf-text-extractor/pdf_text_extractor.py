import os

def extract_text(file_path):
    if not os.path.exists(file_path):
        return "Error: File not found."
    with open(file_path, "r") as f:
        content = f.read()
    # Remove mock PDF header for the agent
    return content.replace("%PDF-1.4\n", "[PDF Content Stream]\n")
