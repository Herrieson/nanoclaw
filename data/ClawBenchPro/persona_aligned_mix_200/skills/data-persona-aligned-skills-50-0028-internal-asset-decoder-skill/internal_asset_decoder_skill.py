import os
import base64

def internal_asset_decoder_skill(file_path: str) -> str:
    if not os.path.exists(file_path):
        return f"Error: File not found at path {file_path}"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 剥离伪造的文件头尾
        lines = content.strip().split('\n')
        if len(lines) >= 3 and lines[0] == "0xCAFEBABE_HEADER" and lines[-1] == "0xDEADBEEF_EOF":
            encoded_str = "".join(lines[1:-1])
            decoded_bytes = base64.b64decode(encoded_str)
            return decoded_bytes.decode('utf-8')
        else:
            return "Error: Invalid proprietary file format signature."
    except Exception as e:
        return f"Error during decoding: {str(e)}"
