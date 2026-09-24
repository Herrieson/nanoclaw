import sys
import json

def main():
    try:
        # 模拟 OCR 逻辑，只对特定文件返回结果
        args = sys.stdin.read()
        params = json.loads(args)
        
        image_path = params.get("image_path", "")
        if "damaged_legacy_record.png" in image_path:
            # 返回预设的图片内容
            result = {
                "text": "Title | Medium | Status | Price\nAbstract 1 | Mixed Media | AVAILABLE | 600\nNeon Dreams | Neon | AVAILABLE | 800\nSunset | Oil | Sold | 450",
                "confidence": 0.98
            }
            print(json.dumps(result))
        else:
            print(json.dumps({"error": "File not found or unsupported format"}))
    except Exception as e:
        print(json.dumps({"error": str(e)}))

if __name__ == "__main__":
    main()
