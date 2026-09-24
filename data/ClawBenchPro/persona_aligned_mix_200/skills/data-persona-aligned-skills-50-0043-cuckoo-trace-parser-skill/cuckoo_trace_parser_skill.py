import os
import zlib

def cuckoo_trace_parser_skill(file_path: str) -> str:
    """
    Parses a proprietary .ctx sandbox trace file and returns its plaintext content.
    """
    if not os.path.exists(file_path):
        return f"Error: File not found at '{file_path}'"
        
    try:
        with open(file_path, "rb") as f:
            data = f.read()
            
        # Verify the proprietary header
        if not data.startswith(b"CTX_V3\x00\x00"):
            return "Error: Invalid file format. The file is not a valid Cuckoo CTX V3 file."
            
        # Extract and decompress the payload
        compressed_payload = data[8:]
        plaintext = zlib.decompress(compressed_payload).decode("utf-8")
        
        return plaintext
    except Exception as e:
        return f"System Error during parsing: {str(e)}"
