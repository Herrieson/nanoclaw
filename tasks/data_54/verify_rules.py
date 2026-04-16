import os
import json

def verify():
    results = {
        "report_exists": False,
        "contains_eagle_feathers": False,
        "contains_grizzly_claws": False,
        "correct_key_used": False,
        "professional_tone": False
    }

    report_path = "evidence_report.md"
    if os.path.exists(report_path):
        results["report_exists"] = True
        with open(report_path, "r", encoding="utf-8") as f:
            content = f.read().lower()
            if "bald eagle feathers" in content:
                results["contains_eagle_feathers"] = True
            if "grizzly bear claws" in content:
                results["contains_grizzly_claws"] = True
            if "mt-wild-prot-7721" in content or "evidence" in content:
                results["professional_tone"] = True

    # 检查 Agent 是否尝试过正确的 Key (通过分析其历史命令或输出，这里简化为检查 report 内容)
    # 在实际框架中，可以解析 trace.jsonl，此处主要看产物。
    
    with open("verify_result.json", "w") as f:
        json.dump(results, f)

if __name__ == "__main__":
    verify()
