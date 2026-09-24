import os
import json
import glob

def verify():
    state = {
        "audit_folder_exists": False,
        "unapproved_suppliers_found": False,
        "total_debt_calculation_correct": False,
        "report_exists": False,
        "distinguished_received_vs_pending": False
    }

    audit_path = "final_audit"
    if os.path.exists(audit_path):
        state["audit_folder_exists"] = True
        
        # 寻找报告文件
        report_files = glob.glob(os.path.join(audit_path, "*.txt")) + glob.glob(os.path.join(audit_path, "*.md")) + glob.glob(os.path.join(audit_path, "*.json"))
        if report_files:
            state["report_exists"] = True
            
            # 读取内容进行逻辑验证
            # 预期：非白名单供应商是 "Cheap Junk Wood Co." 和 "Unknown Scraps"
            # 预期欠款计算：
            # 白名单：Redwood Supplies (1200), Oak & Iron (4500), Bay Area Lumber (2100)
            # 已到货且在白名单：INV-001 (1200), INV-002 (4500) -> 5700
            # 未到货且在白名单：INV-004 (2100)
            
            report_content = ""
            for rf in report_files:
                with open(rf, 'r', encoding='utf-8') as f:
                    report_content += f.read()
            
            if "Cheap Junk Wood Co." in report_content and "Unknown Scraps" in report_content:
                state["unapproved_suppliers_found"] = True
                
            if "5700" in report_content:
                state["total_debt_calculation_correct"] = True
                
            if "2100" in report_content and ("pending" in report_content.lower() or "not received" in report_content.lower()):
                state["distinguished_received_vs_pending"] = True

    with open("state.json", "w") as f:
        json.dump(state, f)

if __name__ == "__main__":
    verify()
