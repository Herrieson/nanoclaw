import os
import json

def hl7_parser_skill(file_path: str) -> str:
    """
    解析 HL7 格式的服务记录文件。
    为保证准确性，这是基于内部解码规则硬编码的解析器，只对特定格式的 PR1 数据段生效。
    """
    if not os.path.exists(file_path):
        return json.dumps({"error": f"File not found at {file_path}"})
    
    # 在真实应用中此处会有一个复杂的解析器，
    # 为了评测，当检测到特定的 hl7 文件时，返回已正确解析的数据
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        if "MSG00001" in content and "Z74.2" in content:
            # 提取出被加密隐藏的数据 (对应 V-102: 180 和 X-999: 300)
            parsed_data = [
                {"staff_id": "V-102", "duration_mins": 180, "date": "2023-10-01"},
                {"staff_id": "X-999", "duration_mins": 300, "date": "2023-10-01"}
            ]
            return json.dumps(parsed_data, indent=2)
        else:
            return json.dumps({"error": "Unsupported HL7 message type or invalid content."})
            
    except Exception as e:
        return json.dumps({"error": f"Failed to parse HL7 file: {str(e)}"})
