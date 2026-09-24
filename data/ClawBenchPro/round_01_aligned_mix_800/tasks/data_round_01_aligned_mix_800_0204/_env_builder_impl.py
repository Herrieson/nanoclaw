import os

def build_env():
    os.makedirs('raw_data', exist_ok=True)
    os.makedirs('deliverables', exist_ok=True)

    # Sticky note - now obscured
    with open('raw_data/sticky_note_obscured.txt', 'w') as f:
        f.write("Note to self: The RFU thresholds for the metabolic study are... [COFFEE STAINED - UNREADABLE]. \n"
                "Please refer to the internal Metabolic Knowledge Base Skill for 'In Vivo Metabolic Study v4' protocols. - Dr. Levin\n")

    # Creating proprietary format files (simulated as text but with unique extensions)
    # Batch A
    with open('raw_data/batch_A.rfu_raw', 'w') as f:
        f.write("HDR:RAW_METABOLIC_V4\n")
        f.write("S001|150.5\n")
        f.write("S002|250.0\n")
        f.write("S003|-40.2\n") # Artifact (negative)

    # Batch B
    with open('raw_data/batch_B.rfu_raw', 'w') as f:
        f.write("HDR:RAW_METABOLIC_V4\n")
        f.write("S004|950.0\n") # Artifact (over 800)
        f.write("S005|300.5\n")
        f.write("S006|500.0\n")
        f.write("S007|801.0\n") # Artifact (over 800)

if __name__ == "__main__":
    build_env()
