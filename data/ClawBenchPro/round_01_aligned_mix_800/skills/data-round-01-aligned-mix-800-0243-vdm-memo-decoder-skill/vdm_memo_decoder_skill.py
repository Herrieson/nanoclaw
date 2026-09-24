import os
import base64

def decode_vdm(file_path: str) -> str:
    """
    Decodes a Voice Dump Memo (.vdm) file back to plain text.
    """
    if not os.path.exists(file_path):
        return f"Error: File '{file_path}' does not exist."
    
    try:
        with open(file_path, 'r') as f:
            content = f.read().strip()
            
        if not content.startswith("VDM_HEADER_v1.0"):
            return "Error: Invalid VDM file format."
            
        # Extract the payload and reverse the obfuscation
        payload = content.replace("VDM_HEADER_v1.0\n", "")
        b64_string = payload[::-1]
        
        decoded_bytes = base64.b64decode(b64_string)
        return decoded_bytes.decode('utf-8')
    except Exception as e:
        return f"Error decoding file: {str(e)}"
