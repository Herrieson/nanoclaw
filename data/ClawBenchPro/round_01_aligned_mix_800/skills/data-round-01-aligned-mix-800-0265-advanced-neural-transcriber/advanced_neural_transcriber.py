import os

def transcribe(file_path):
    """
    Decodes the raw .dat files into readable dispatch text.
    """
    if not os.path.exists(file_path):
        return "Error: File not found."
    
    with open(file_path, "r") as f:
        raw = f.read()
    
    # Mocking the transcription logic
    if "friday" in file_path:
        return "20:00 - Dispatch 104. Noise complaint at Elm St. Subject: Carlos Mendez. \n22:30 - Dispatch 108. Public intoxication. Subject: Elena Rostova."
    elif "saturday" in file_path:
        return "09:15 - Dispatch 201. Illegal dumping reported. Suspect: Sarah Smith. \n14:20 - Dispatch 215. Shoplifting. Subject: Jimmy O'Connor."
    elif "sunday" in file_path:
        return "02:10 - Dispatch 305. Noise complaint. Subject: Miguel Santos. \n23:45 - Dispatch 240. Noise complaint. Subject: Bob Builder."
    else:
        return "Error: Unknown data format or corrupted audio."
