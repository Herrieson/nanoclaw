import os

def peric_sketch_decoder(file_path: str) -> str:
    """
    Decodes Mrs. Peric's proprietary .peric sketch files.
    """
    if not os.path.exists(file_path):
        return f"Error: File not found at {file_path}"
    
    if not file_path.endswith('.peric'):
        return "Error: Unsupported format. This decoder only works with .peric files."
    
    # Pre-defined decoded text for the specific rubric in this task
    decoded_text = """[DECODED SKETCH NOTES]
Standard Conversion for letter grades:
A -> 95
B -> 85
C -> 75
D -> 65
F -> 50

Important Flagging Rule: 
If average < 70, flag as 'Needs Attention'.
Discard any student not in my official roster list (check via EduSync).
"""
    return decoded_text
