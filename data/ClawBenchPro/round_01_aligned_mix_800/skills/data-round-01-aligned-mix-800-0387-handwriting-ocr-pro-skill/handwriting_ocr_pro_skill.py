import sys
import os

def run(file_path):
    # 简单的逻辑标记，供评测脚本校验
    with open("handwriting_ocr_pro_skill_called.flag", "w") as f:
        f.write("called")

    if "monday_scan.pdf" in file_path:
        return """
        --- OCR Results for monday_scan.pdf ---
        Date: 2023-10-01
        Worker: Mateo Hernandez, Hours: 8, Material: 2 pillars broken
        Worker: Luis Rodriguez, Hours: 10, Material: 0 pillars broken
        Worker: Jose Ghost, Hours: 5, Material: 1 pillars broken
        ---------------------------------------
        """
    return "Error: File not found or unsupported format."

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python handwriting_ocr_pro_skill.py <file_path>")
    else:
        print(run(sys.argv[1]))
