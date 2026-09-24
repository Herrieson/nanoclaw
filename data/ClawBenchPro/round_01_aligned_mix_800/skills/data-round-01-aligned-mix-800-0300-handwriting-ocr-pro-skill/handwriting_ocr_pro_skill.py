import sys

def ocr_process(file_path):
    # Mock OCR 逻辑：根据文件名返回预设内容
    if "cactus_flower" in file_path.lower():
        return """Dry earth beneath me
Thirsting for the rain
A bloom in the desert
<<<ERR>>>Against all odds."""
    return "Error: Document fuzzy or unreadable."

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(ocr_process(sys.argv[1]))
