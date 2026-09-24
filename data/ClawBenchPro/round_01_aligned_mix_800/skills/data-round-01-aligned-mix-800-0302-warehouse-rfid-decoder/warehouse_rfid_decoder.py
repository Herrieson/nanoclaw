import os
import json
import base64

def decode_rfid_file(file_path: str):
    """
    解析带有特定 Header 的混淆 RFID 数据文件。
    """
    if not os.path.exists(file_path):
        return f"Error: File '{file_path}' does not exist."
    
    try:
        with open(file_path, "rb") as f:
            content = f.read()
            
        # 寻找真实的 Base64 起始位置
        # 头部可能包含 "RFID_SCAN_V2_MAGIC_HEADER_0x8F\n"
        if b'\n' in content:
            _, payload = content.split(b'\n', 1)
        else:
            payload = content
            
        decoded_bytes = base64.b64decode(payload)
        decoded_str = decoded_bytes.decode('utf-8')
        
        # 转换回 JSON 对象
        data = json.loads(decoded_str)
        return data
        
    except json.JSONDecodeError:
        return "Error: Decoding failed. Corrupted payload structure."
    except Exception as e:
        return f"System Error during RFID parsing: {str(e)}"
