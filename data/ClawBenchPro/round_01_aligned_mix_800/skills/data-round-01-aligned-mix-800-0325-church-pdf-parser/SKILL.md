---
name: "church_pdf_parser"
description: "专门用于解析教区安全加密格式 PDF 的阅读器。"
aliases:
  - church_pdf_parser
  - data-round-01-aligned-mix-800-0325-church-pdf-parser
---

# church_pdf_parser
专门用于解析教区安全加密格式 PDF 的阅读器。

## 功能说明
这个工具将教区内部的文档、牧师语音备忘转录 PDF 转化为干净的明文。由于教区使用了老式的加密算法，标准的第三方 Python 库可能无法直接读取这些文件。

## 参数
- `file_path` (string): 必须提供，指向需要解析的 PDF 文件路径（例如: `attendance_logs/pastor_voice_memo.pdf`）

## 返回值
(string) PDF 文档中解密出的明文内容。
