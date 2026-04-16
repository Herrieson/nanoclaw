import os
import random

def build_env():
    base_dir = "assets/data_427/messy_desk"
    os.makedirs(base_dir, exist_ok=True)
    
    # Patient Data (varying formats)
    patients = [
        "Patient: Liam Nelson | Diagnosis: Childhood Apraxia of Speech",
        "Pt: Sarah Jenkins - Diag: Dysphagia",
        "[PATIENT] Marcus Thorne [DIAGNOSIS] Aphasia",
        "Patient Name: Emily Clark, Diagnosis: Stuttering",
        "PT: David Kim ; DIAG: Spasmodic Dysphonia",
        "Patient: Olivia Wilde | Diagnosis: Dysarthria",
        "Pt: James Holden - Diag: Receptive Language Disorder"
    ]
    
    # Petition Data
    petitions = [
        "Signee: John Doe - Universal Healthcare NOW!",
        "Signature: Amanda Smith - Medicare for All",
        "Signee: Robert Baratheon - Community Health Centers Funding",
        "Signature: Ned Stark - Protect the ACA"
    ]
    
    # Knitting Patterns
    patterns = [
        "Pattern: Basic Scarf\nRow 1: Knit all.\nRow 2: Purl all.",
        "Pattern: Chunky Beanie\nCast on 40 stitches. Knit in the round.",
        "--- BEGIN ALPACA CARDIGAN ---\nYarn: 100% Baby Alpaca, Worsted weight\nNeedles: US 8 (5.0 mm)\nGauge: 18 sts = 4 inches in stockinette\nInstructions:\nCast on 120 sts. Work in 1x1 rib for 2 inches.\nSwitch to stockinette and work until piece measures 15 inches.\nDivide for armholes...\n--- END ALPACA CARDIGAN ---",
        "Pattern: Wool Socks\nCuff down, heel flap and gusset."
    ]

    # Mix them up into multiple files
    all_lines = patients + petitions + patterns
    
    # Add some random junk
    junk = [
        "Need to buy more almond milk.",
        "Call Mom back.",
        "Did it rain today? Classic PNW.",
        "Meeting at 3PM with HR.",
        "Don't forget to breathe."
    ]
    
    all_content = all_lines + junk
    random.seed(42)
    random.shuffle(all_content)
    
    # Split into 3 files
    chunks = [all_content[:6], all_content[6:12], all_content[12:]]
    filenames = ["notes_monday_final.txt", "backup_archive.log", "mixed_dump.dat"]
    
    for filename, chunk in zip(filenames, chunks):
        with open(os.path.join(base_dir, filename), "w", encoding="utf-8") as f:
            for item in chunk:
                f.write(item + "\n\n")

if __name__ == "__main__":
    build_env()
