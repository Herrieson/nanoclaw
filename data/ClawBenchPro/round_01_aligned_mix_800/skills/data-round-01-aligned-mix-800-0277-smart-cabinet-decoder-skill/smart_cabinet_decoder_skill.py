import sys
import base64

def decode_mcl(filepath):
    try:
        with open(filepath, 'r') as f:
            encoded_content = f.read().strip()
            
        if not encoded_content.startswith("MCL_SECURE_FORMAT_"):
            return "Error: Invalid MCL format. File must contain the OmniCell header."
        
        # Extract the base64 payload
        payload = encoded_content.replace("MCL_SECURE_FORMAT_", "")
        decoded_text = base64.b64decode(payload).decode('utf-8')
        
        print("--- DECODED OMNICELL CABINET LOGS ---")
        print(decoded_text)
        
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found.")
    except Exception as e:
        print(f"Failed to decode cabinet logs: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python smart_cabinet_decoder_skill.py <path_to_mcl_file>")
    else:
        decode_mcl(sys.argv[1])
