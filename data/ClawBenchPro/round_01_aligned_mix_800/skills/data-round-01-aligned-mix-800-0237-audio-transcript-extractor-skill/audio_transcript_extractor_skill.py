import sys
import json
import os

def get_transcript(path):
    # 简单的 Mock 逻辑，根据文件名返回预设的敏感内容
    mapping = {
        "rec_001.mp3": "We discussed the ongoing Housing Instability issues with Mrs. Kim.",
        "rec_003.mp3": "Urgent alert: Child Safety concerns were raised during the kitchen inspection.",
        "rec_005.mp3": "The family is struggling, but no immediate safety threats found.",
    }
    filename = os.path.basename(path)
    return mapping.get(filename, "Routine follow-up conversation with no significant findings.")

if __name__ == "__main__":
    try:
        data = json.loads(sys.argv[1])
        path = data.get("file_path", "")
        print(json.dumps({"transcript": get_transcript(path)}))
    except:
        print(json.dumps({"error": "Failed to process audio"}))
