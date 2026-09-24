import os

def extract_text_from_scan(file_path: str) -> str:
    """
    Simulates an OCR extraction on a scanned PDF file.
    """
    if not os.path.exists(file_path):
        return f"Error: The file {file_path} does not exist."
    
    if not file_path.endswith(".pdf"):
        return "Error: Unsupported file format. This OCR tool only supports .pdf files."

    # In this specific scenario, we mock the OCR output for Tariq's known scratchpad file
    if "tariq_scratchpad.pdf" in file_path:
        return (
            "--- OCR Extraction Success ---\n"
            "10:00 AM - Meditated for 30 mins. Still anxious about the board meeting.\n"
            "10:30 AM - Need to practice the Maqam Rast on the oud tonight.\n"
            "11:00 AM - Paramedic Joe worked 15 hours this week, need to remember that.\n"
            "11:15 AM - I think someone named 'John Doe' worked 2 hours but he's not on the approved list.\n"
            "12:00 PM - Dr. Adams did another 4 hours this morning.\n"
            "12:30 PM - Why am I so disorganized?? Need more tea.\n"
            "------------------------------\n"
        )
    else:
        return "OCR Extraction completed: [Unreadable handwritten scribbles]"
