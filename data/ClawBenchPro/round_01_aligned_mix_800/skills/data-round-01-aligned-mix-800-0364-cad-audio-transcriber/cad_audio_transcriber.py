import os

def parse_cad(file_path):
    if not os.path.exists(file_path):
        return f"Error: File '{file_path}' not found."
    
    if not file_path.endswith('.cad'):
        return "Error: Unsupported format. This tool only transcibes .cad files."

    # Mocked transcription logic mapping file paths to transcripts
    base_name = os.path.basename(file_path)
    
    transcripts_db = {
        "depo_20231001_smith.cad": "DEPOSITION TRANSCRIPT\nCase: Smith v. State\nDate: 2023-10-01\nPresent: Siobhan O'Malley, Witness A.\nText: [Audio clear] The witness states...",
        "depo_20231002_smith_extra.cad": "DEPOSITION TRANSCRIPT\nCase: Smith v. State\nDate: 2023-10-02\nPresent: Paralegal Miller, Witness B.\nNote: Unscheduled session. [Audio muffled].",
        "depo_20231002_doe.cad": "DEPOSITION TRANSCRIPT\nCase: Doe v. City\nDate: 2023-10-02\nPresent: Siobhan O'Malley.\nText: [Audio clear] Proceeding with the Doe deposition..."
    }

    if base_name in transcripts_db:
        return transcripts_db[base_name]
    else:
        return "DEPOSITION TRANSCRIPT\n[Error: Audio file corrupted or empty.]"

def execute(file_path):
    return parse_cad(file_path)
