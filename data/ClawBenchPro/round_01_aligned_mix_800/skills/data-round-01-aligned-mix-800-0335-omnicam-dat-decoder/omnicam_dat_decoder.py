import os
import base64

def omnicam_dat_decoder(file_path: str) -> str:
    """
    Decodes OmniCam .dat files by skipping the proprietary magic header
    and decoding the base64 payload.
    """
    if not os.path.exists(file_path):
        return f"Error: File not found at {file_path}"
    
    try:
        with open(file_path, "rb") as f:
            content = f.read()
            
        # Check for proprietary header
        header = b"OMNICAM_V2_MAGIC\n"
        if not content.startswith(header):
            return "Error: Invalid OmniCam .dat file format or missing magic header."
            
        payload = content[len(header):]
        decoded_str = base64.b64decode(payload).decode("utf-8")
        return decoded_str
        
    except Exception as e:
        return f"Decoding Exception: {str(e)}"
