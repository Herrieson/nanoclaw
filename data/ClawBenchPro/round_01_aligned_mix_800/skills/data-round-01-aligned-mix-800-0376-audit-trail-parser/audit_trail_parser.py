import os
import base64

def parse_audit_trail(file_path):
    """
    Reads a proprietary binary audit file, strips the header, and decodes the content.
    """
    if not os.path.exists(file_path):
        return f"Error: File not found at {file_path}"
        
    try:
        with open(file_path, "rb") as f:
            content = f.read()
            
        # The proprietary format uses a 10-byte magic header: \x89AUDIT\x0d\x0a\x1a\x0a
        if not content.startswith(b"\x89AUDIT\x0d\x0a\x1a\x0a"):
            return "Error: Invalid file format. Missing proprietary audit magic header."
            
        # Strip the first 10 bytes
        payload = content[10:]
        
        # Decode the base64 payload
        decoded_text = base64.b64decode(payload).decode('utf-8')
        return f"--- PARSED DATA ---\n{decoded_text}"
        
    except Exception as e:
        return f"System Error during parsing: {str(e)}"
