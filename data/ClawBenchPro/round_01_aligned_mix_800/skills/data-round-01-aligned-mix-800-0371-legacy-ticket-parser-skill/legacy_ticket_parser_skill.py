import base64
import csv
import io

def legacy_ticket_parser_skill(file_path: str):
    try:
        with open(file_path, "rb") as f:
            encoded_content = f.read()
        
        # Step 1: Base64 decode
        decoded_bytes = base64.b64decode(encoded_content)
        
        # Step 2: UTF-16 decode
        decoded_text = decoded_bytes.decode("utf-16")
        
        # Step 3: Parse CSV
        f_obj = io.StringIO(decoded_text)
        reader = csv.DictReader(f_obj)
        return list(reader)
    except Exception as e:
        return {"error": f"Failed to parse legacy file: {str(e)}"}
