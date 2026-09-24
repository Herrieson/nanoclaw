import os

def ocr_handwritten_vision_log_skill(file_path):
    """
    Simulates OCR extraction from the provided PDF path.
    """
    if not os.path.exists(file_path):
        return "Error: File not found."
    
    # Mocking the OCR result for the specific task context
    mock_data = """
    --- HANDWRITTEN LOG: OCT 1st EVENT ---
    1. Alice Smith - (Prescription check)
    2. bob jones - (Browsing eco-frames)
    3. Charlie Brown - (Brought own frames)
    4. DIANA PRINCE - (Waiting for exam)
    5. Evan Wright - (Looking for sunglasses)
    """
    return mock_data
