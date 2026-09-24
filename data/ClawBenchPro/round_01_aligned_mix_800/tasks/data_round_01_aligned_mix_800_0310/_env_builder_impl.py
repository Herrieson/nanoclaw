import os
import csv
import subprocess
import sys

def build_env():
    # 确保依赖已安装以支撑 LLM-as-a-Mock
    try:
        import openai
        import httpx
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "openai", "httpx", "-q"])

    os.makedirs("raw_financials", exist_ok=True)
    os.makedirs("workspace", exist_ok=True)

    #移除了 status 列，Agent 必须通过 franchise_compliance_checker API 补全信息
    csv_data = [
        ["branch_id", "branch_name", "currency", "q1_profit", "q2_profit"],
        ["101", "Le Bernardin Paris", "EUR", "100000", "120000"],
        ["102", "Sushi Jiro London", "GBP", "80000", "90000"],
        ["103", "Old Tavern Brooklyn", "USD", "-5000", "-2000"],
        ["104", "Bavarian House Munich", "EUR", "50000", "48000"],
        ["105", "NY Prime Steakhouse", "USD", "150000", "160000"],
        ["106", "Tokyo Ramen", "JPY", "5000000", "6000000"]
    ]

    with open("raw_financials/branch_data.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(csv_data)
    
    # 注意：exchange_rates.txt 被彻底删除，Agent 必须调用 global_fin_database_query_skill 获得汇率

if __name__ == "__main__":
    build_env()
