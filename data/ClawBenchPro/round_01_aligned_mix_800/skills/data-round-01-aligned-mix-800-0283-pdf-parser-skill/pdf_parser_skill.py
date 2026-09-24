import sys
import os

def parse_pdf(file_path):
    if not os.path.exists(file_path):
        return f"Error: File {file_path} not found."
    
    # 模拟 PDF 解析逻辑：实际环境中读取内容
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        return content
    except Exception as e:
        return f"Error parsing PDF: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python pdf_parser_skill.py <file_path>")
    else:
        print(parse_pdf(sys.argv[1]))
