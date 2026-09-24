import base64
import os

def geth_rpc_trace_decoder(file_path: str) -> str:
    """
    Decodes the custom EVMSNAP binary format into a JSON string.
    """
    if not os.path.exists(file_path):
        return f"Error: File '{file_path}' does not exist."
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Verify custom header
        if not content.startswith("EVMSNAP\x00\x01\n"):
            return "Error: Invalid file format. Missing EVMSNAP magic header."
            
        # Extract payload
        payload_b64 = content.split("\n", 1)[1]
        
        # Decode base64
        json_data = base64.b64decode(payload_b64).decode('utf-8')
        
        return json_data
        
    except Exception as e:
        return f"Error decoding trace file: {str(e)}"
