import os

def scan_memory(file_path: str, magic_hex: str, extract_length: int) -> str:
    """
    Scans a binary dump file for a magic hex string and extracts following bytes.
    """
    if not os.path.exists(file_path):
        return f"Error: File not found at {file_path}"
    
    if extract_length <= 0:
        return "Error: extract_length must be greater than 0."

    # Clean the hex string
    clean_hex = magic_hex.replace(" ", "").replace("0x", "").upper()
    try:
        magic_bytes = bytes.fromhex(clean_hex)
    except ValueError:
        return "Error: Invalid hexadecimal string provided."

    try:
        with open(file_path, "rb") as f:
            data = f.read()
            
        index = data.find(magic_bytes)
        if index == -1:
            return f"Result: Magic signature {clean_hex} not found in the memory dump."
            
        start_pos = index + len(magic_bytes)
        end_pos = start_pos + extract_length
        
        if start_pos >= len(data):
            return "Error: Magic signature found at the end of the file, no trailing bytes to extract."
            
        extracted_bytes = data[start_pos : end_pos]
        hex_result = " ".join([f"{b:02X}" for b in extracted_bytes])
        
        return hex_result
        
    except Exception as e:
        return f"System Error: Failed to process the memory dump. Details: {str(e)}"
