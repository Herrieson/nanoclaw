import os
import json

def verify():
    results = {
        "accounting_dir_exists": os.path.exists("accounting"),
        "summary_report_exists": False,
        "rejection_list_exists": False,
        "purity_logic_correct": False,
        "valuation_correct": False,
        "deduplication_performed": False
    }

    # 1. 检查汇总报告
    summary_path = ""
    for f in os.listdir("accounting") if results["accounting_dir_exists"] else []:
        if "汇总" in f or "summary" in f.lower() or "valuation" in f.lower():
            summary_path = os.path.join("accounting", f)
            results["summary_report_exists"] = True
            break

    # 2. 检查拒绝清单
    rejection_path = ""
    for f in os.listdir("accounting") if results["accounting_dir_exists"] else []:
        if any(x in f.lower() for x in ["reject", "垃圾", "次品", "unqualified", "failed"]):
            rejection_path = os.path.join("accounting", f)
            results["rejection_list_exists"] = True
            break

    # 3. 验证数据逻辑 (核心校验)
    # 即使改变了技能调用方式，底层的标准答案应当保持一致以确保业务结果：
    # B002(82%), B004(78.2%), B007(84.5%) 应该在拒绝名单
    # 汇总：Copper=1650kg ($14025), Zinc=2000kg ($4800), Nickel=1100kg ($17820)
    
    try:
        if results["rejection_list_exists"]:
            with open(rejection_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if "B002" in content and "B004" in content and "B007" in content:
                    results["purity_logic_correct"] = True
        
        if results["summary_report_exists"]:
            with open(summary_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # 检查 Copper 的总价值和重量是否计算正确
                if "1650" in content and "14025" in content:
                    results["valuation_correct"] = True
                # 检查去重情况 (B001 不应被计算两次)
                if "2850" not in content: # 如果没有去重，Copper 会是 1200+1200+450=2850
                    results["deduplication_performed"] = True
    except Exception:
        pass

    with open("state.json", "w") as f:
        json.dump(results, f)

if __name__ == "__main__":
    verify()
