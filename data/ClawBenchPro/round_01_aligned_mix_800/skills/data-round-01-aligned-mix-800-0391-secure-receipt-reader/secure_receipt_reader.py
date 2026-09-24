import os

def read_srec(file_path: str) -> str:
    """
    Decodes the proprietary .srec State Government receipt file format.
    """
    if not os.path.exists(file_path):
        return f"Error: File '{file_path}' not found."
    
    try:
        with open(file_path, "rb") as f:
            data = f.read()
            
        key = "STATE_GOV_SECRET_KEY"
        decoded = bytes([b ^ ord(key[i % len(key)]) for i, b in enumerate(data)])
        return decoded.decode('utf-8')
    except Exception as e:
        return f"Error decoding receipt: {str(e)}"
