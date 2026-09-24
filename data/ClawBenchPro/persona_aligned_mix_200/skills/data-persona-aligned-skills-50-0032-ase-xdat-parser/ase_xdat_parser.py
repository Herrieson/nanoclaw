import base64
import json
import os

def ase_xdat_parser(file_path: str):
    if not os.path.exists(file_path):
        return {"error": f"File {file_path} not found."}
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        if len(lines) < 2 or "XDAT_TRAJ" not in lines[0]:
            return {"error": "Invalid file format. Not a recognized XDAT trajectory."}
            
        encoded_content = "".join(lines[1:])
        decoded_bytes = base64.b64decode(encoded_content)
        traj_data = json.loads(decoded_bytes.decode('utf-8'))
        
        return traj_data
    except Exception as e:
        return {"error": f"Failed to parse trajectory: {str(e)}"}
