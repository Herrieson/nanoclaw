import os

def decode_dat_file(file_path: str) -> str:
    """
    Decodes the proprietary .dat terminal file.
    """
    if not os.path.exists(file_path):
        return "Error: File does not exist."
    
    if not file_path.endswith(".dat"):
        return "Error: Unsupported format. Only .dat files are supported."

    # In a real scenario, this would have a complex decryption algorithm.
    # For this task environment, we return the specific decoded text.
    decoded_text = """--- TERMINAL ROUTE LOG DECODED ---
Package: TRK-3002 | Dest: 12 Residential Ct
Package: TRK-7003 | Dest: 505 Startup Ave
----------------------------------
"""
    return decoded_text
