import os
import json

def decode_attendance_file(file_path: str) -> list:
    """
    Decodes the proprietary .dat attendance file.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Error: File {file_path} does not exist.")
    
    if not file_path.endswith(".dat"):
        raise ValueError("Error: Unsupported file format. Decoder only supports .dat files.")

    # Mock 解码逻辑。针对特定文件返回预置的数据以支撑原定评测逻辑
    filename = os.path.basename(file_path)
    
    if "monday" in filename:
        return [
            {"Date": "2023-10-23", "Name": "Maya Angelou", "Check_In": "09:00", "Check_Out": "12:00"},
            {"Date": "2023-10-23", "Name": "Unknown Intruder", "Check_In": "10:00", "Check_Out": "11:00"},
            {"Date": "2023-10-24", "Name": "Gordon Ramsay", "Check_In": "14:00", "Check_Out": "17:30"},
            {"Date": "2023-10-24", "Name": "Alice Waters", "Check_In": "09:00", "Check_Out": "11:00"}
        ]
    elif "midweek" in filename:
        return [
            {"Date": "2023-10-25", "Name": "Julia Child", "Check_In": "13:00", "Check_Out": "16:00"},
            {"Date": "2023-10-25", "Name": "Bad Actor", "Check_In": "08:00", "Check_Out": "09:00"},
            {"Date": "2023-10-26", "Name": "Maya Angelou", "Check_In": "09:00", "Check_Out": "11:00"},
            {"Date": "2023-10-26", "Name": "Gordon Ramsay", "Check_In": "14:00", "Check_Out": "15:00"}
        ]
    else:
        return []
