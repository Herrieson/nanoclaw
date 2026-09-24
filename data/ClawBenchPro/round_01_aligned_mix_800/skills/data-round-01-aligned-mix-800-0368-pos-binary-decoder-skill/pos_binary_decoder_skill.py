import sys
import struct
import json

def decode_bdat(filepath):
    try:
        with open(filepath, 'rb') as f:
            header = f.read(8)
            if header != b'POS_BDAT':
                return json.dumps({"error": "Not a valid POS_BDAT file. Missing header."})
            
            length_data = f.read(4)
            if not length_data:
                return json.dumps({"error": "File corrupted. Cannot read length."})
            
            length = struct.unpack('>I', length_data)[0]
            obfuscated_data = f.read(length)
            
            # Decrypt payload (XOR 0x42 operation used by legacy system)
            json_bytes = bytes([b ^ 0x42 for b in obfuscated_data])
            
            try:
                data = json.loads(json_bytes.decode('utf-8'))
                return json.dumps(data, indent=2)
            except json.JSONDecodeError:
                return json.dumps({"error": "Decrypted data is not valid JSON."})
                
    except FileNotFoundError:
        return json.dumps({"error": f"File {filepath} not found."})
    except Exception as e:
        return json.dumps({"error": f"Error decoding file: {str(e)}"})

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: python pos_binary_decoder_skill.py <filepath>"}))
        sys.exit(1)
    
    print(decode_bdat(sys.argv[1]))
