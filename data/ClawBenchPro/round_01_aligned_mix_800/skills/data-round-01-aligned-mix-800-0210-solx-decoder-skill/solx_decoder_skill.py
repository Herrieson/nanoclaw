import sys
import base64
import os

def decode_solx(file_path):
    if not os.path.exists(file_path):
        return f"Error: File '{file_path}' does not exist."
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            encoded_content = f.read().strip()
        
        # Obfuscated eco-gadget format is fundamentally a base64 encoded stream
        decoded_bytes = base64.b64decode(encoded_content)
        decoded_string = decoded_bytes.decode('utf-8')
        return decoded_string
    except Exception as e:
        return f"Decoder Error: Could not parse the .solx file. {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python solx_decoder_skill.py <file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    result = decode_solx(file_path)
    print(result)
