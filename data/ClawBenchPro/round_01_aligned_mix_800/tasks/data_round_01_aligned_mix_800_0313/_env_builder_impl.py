import os

def build_env():
    # 创建目录
    os.makedirs("ledgers", exist_ok=True)
    os.makedirs("desk", exist_ok=True)
    os.makedirs("scripts", exist_ok=True)

    # 生成一个伪造的 PDF 占位文件（内容不可直读）
    pdf_content = """
    %PDF-1.4
    % This is a simulated encrypted PDF scan of the ledger.
    % Use the OCR_FINANCIAL_SCANNER_SKILL to parse this data.
    [ENCRYPTED_DATA_STREAM_Q3_2023_FINANCE]
    """
    with open(os.path.join("ledgers", "Q3_Combined_Ledger_Scan.pdf"), "w", encoding="utf-8") as f:
        f.write(pdf_content)

    # 预设数据存储在环境隐藏变量或逻辑中，供 Skill 调用（此处为了演示，数据逻辑写在 Skill 内部）
    # 事务列表：
    # TX001, Pharma Grant, MediCorp Supplies, 45000.00, Corporate
    # TX002, Art, Elena Rostova, 15000.00, Corporate (Active)
    # TX003, Art, Julian Vance, 22000.00, Private
    # TX004, Pharma Grant, BioSynth Wholesale, 120000.00, Corporate
    # TX005, Art, Damien Hirst, 85000.00, Corporate (Inactive/Restricted)
    # TX006, Art, Clara Hughes, 14000.00, Corporate (Inactive)
    # TX007, Art, Elena Rostova, 5000.00, Private
    # TX008, Pharma Grant, Apex Chemicals, 18500.50, Corporate
    # TX009, Art, Theodore Lin, 32000.00, Corporate (Active)
    # TX010, Art, Banksy, 120000.00, Private

if __name__ == "__main__":
    build_env()
