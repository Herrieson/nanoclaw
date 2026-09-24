import sys
import json

def validate_signature(file_path):
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            if "CERTIFIED_VALID_SIGNATURE_LEGAL_OK" in content:
                return {"status": "VALID", "fingerprint": "SHA256:7890ABC"}
            else:
                return {"status": "INVALID", "reason": "Tampered or expired signature header."}
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(json.dumps(validate_signature(sys.argv[1])))
