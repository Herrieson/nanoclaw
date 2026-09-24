import sys

SLANG_MAP = {
    "jale": "work/hours (labor time)",
    "postes": "pillars/columns (structural elements)",
    "chamba": "job/task",
    "roto": "broken/damaged"
}

def run(text):
    text = text.lower()
    found = {k: v for k, v in SLANG_MAP.items() if k in text}
    if found:
        return f"Detected Slang Terms: {found}"
    return "No specific construction slang detected."

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python construction_slang_translator.py <text>")
    else:
        print(run(sys.argv[1]))
