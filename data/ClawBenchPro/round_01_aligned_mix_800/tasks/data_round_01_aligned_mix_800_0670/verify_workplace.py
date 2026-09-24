import os
import sys
import json
import glob
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def llm_judge_content(prompt_text, file_content):
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a strict data validation assistant. Answer ONLY with 'YES' or 'NO'."},
                {"role": "user", "content": f"{prompt_text}\n\n[File Content]:\n{file_content}"}
            ],
            temperature=0
        )
        return "yes" in response.choices[0].message.content.strip().lower()
    except Exception as e:
        print(f"LLM API Error: {e}")
        return False

def map_item_name(k):
    k_lower = str(k).lower()
    if "bean" in k_lower: return "canned beans"
    if "soup" in k_lower: return "canned soup"
    if "bread" in k_lower: return "bread"
    if "milk" in k_lower: return "milk"
    if "blanket" in k_lower: return "blankets"
    return k_lower

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    
    score_details = []
    total_score = 0
    
    # 1. Check Output Directory
    outreach_dir = os.path.join(workspace, "outreach_plan")
    if os.path.isdir(outreach_dir):
        score_details.append({"item": "检查结果目录 outreach_plan 是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "目录成功创建"})
        total_score += 10
    else:
        score_details.append({"item": "检查结果目录 outreach_plan 是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 outreach_plan 目录"})
        
    # 2. Check JSON file format validity
    json_data = None
    json_str = ""
    json_files = glob.glob(os.path.join(outreach_dir, "*.json"))
    if json_files:
        try:
            with open(json_files[0], "r", encoding="utf-8") as f:
                json_str = f.read()
                json_data = json.loads(json_str)
            
            # Accommodate cases where agent wraps dict inside a single-item list
            if isinstance(json_data, list) and len(json_data) == 1 and isinstance(json_data[0], dict):
                json_data = json_data[0]
                
            score_details.append({"item": "生成了格式合法的 .json 结构数据文件", "score": 10, "max_score": 10, "passed": True, "reason": f"成功读取并解析 {os.path.basename(json_files[0])}"})
            total_score += 10
        except Exception as e:
            score_details.append({"item": "生成了格式合法的 .json 结构数据文件", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON解析失败: {e}"})
    else:
        score_details.append({"item": "生成了格式合法的 .json 结构数据文件", "score": 0, "max_score": 10, "passed": False, "reason": "未在目标目录下找到 .json 文件"})

    # 3. Check for specific logical sections
    has_alloc = False
    has_short = False
    alloc_data = None
    short_data = None
    
    if json_data and isinstance(json_data, dict):
        keys_lower = {k.lower(): k for k in json_data.keys()}
        alloc_key = next((keys_lower[k] for k in keys_lower if "allocation" in k), None)
        short_key = next((keys_lower[k] for k in keys_lower if "shortage" in k), None)
            
        if alloc_key:
            has_alloc = True
            alloc_data = json_data[alloc_key]
        if short_key:
            has_short = True
            short_data = json_data[short_key]
            
    if has_alloc and has_short:
        score_details.append({"item": "包含 allocations 和 shortages 逻辑字段区", "score": 10, "max_score": 10, "passed": True, "reason": "成功定位到目标逻辑字段"})
        total_score += 10
    else:
        score_details.append({"item": "包含 allocations 和 shortages 逻辑字段区", "score": 0, "max_score": 10, "passed": False, "reason": "JSON 中缺失 allocations 或 shortages 字段区"})

    # Hard rules and inventory reality check
    reqs = {
        "f-01": {"canned beans": 15, "blankets": 4},
        "f-02": {"canned soup": 25, "bread": 5},
        "f-03": {"canned beans": 40, "milk": 2}
    }
    
    expected_shortages = {
        "canned beans": 5,
        "canned soup": 5,
        "bread": 5,
        "milk": 2
    }
    
    expected_total_alloc = {
        "canned beans": 50,
        "blankets": 4,
        "canned soup": 20,
        "bread": 0,
        "milk": 0
    }

    # 4. Extract and check Shortages
    shortages_perfect = False
    shortages_reason = "未获得有效的短缺数据"
    parsed_short = {}
    
    if has_short:
        if isinstance(short_data, dict):
            for k, v in short_data.items():
                parsed_short[map_item_name(k)] = int(v) if str(v).isdigit() else 0
        elif isinstance(short_data, list):
            for entry in short_data:
                if isinstance(entry, dict):
                    name, val = "", 0
                    for k, v in entry.items():
                        if isinstance(v, (int, float)): val = int(v)
                        elif isinstance(v, str) and v.isdigit(): val = int(v)
                        elif isinstance(v, str): name = v
                    if name: parsed_short[map_item_name(name)] = val

        s_pass = True
        for item, exp_v in expected_shortages.items():
            if parsed_short.get(item, 0) != exp_v:
                s_pass = False
        
        # Ensure no unexpected hallucinatory shortages
        for item, val in parsed_short.items():
            if val > 0 and expected_shortages.get(item, 0) != val:
                s_pass = False

        if s_pass:
            shortages_perfect = True
            shortages_reason = "精准去除了 spoiled 和 expired 物品，Shortages 短缺数值计算 100% 正确"
        else:
            shortages_reason = f"Shortages 计算包含错误数据或未正确过滤变质物品。预期值: {expected_shortages}, 实际值提取: {parsed_short}"

    if shortages_perfect:
        score_details.append({"item": "过滤脏数据后计算出准确的 Shortages", "score": 30, "max_score": 30, "passed": True, "reason": shortages_reason})
        total_score += 30
    else:
        score_details.append({"item": "过滤脏数据后计算出准确的 Shortages", "score": 0, "max_score": 30, "passed": False, "reason": shortages_reason})

    # 5. Extract and check Allocations
    allocations_perfect = False
    alloc_reason = "未获得有效的分配数据"
    parsed_alloc = {}
    
    if has_alloc:
        if isinstance(alloc_data, dict):
            for k, v in alloc_data.items():
                fam_id = str(k).lower().strip()
                parsed_alloc[fam_id] = {}
                if isinstance(v, dict):
                    for item, count in v.items():
                        parsed_alloc[fam_id][map_item_name(item)] = int(count) if str(count).isdigit() else 0
                elif isinstance(v, list):
                    for entry in v:
                        if isinstance(entry, dict):
                            iname, ival = "", 0
                            for ek, ev in entry.items():
                                if isinstance(ev, (int, float)): ival = int(ev)
                                elif isinstance(ev, str) and ev.isdigit(): ival = int(ev)
                                elif isinstance(ev, str): iname = ev
                            if iname: parsed_alloc[fam_id][map_item_name(iname)] = ival
        elif isinstance(alloc_data, list):
            for entry in alloc_data:
                if isinstance(entry, dict):
                    fam_id = None
                    for k, v in entry.items():
                        if "family" in str(k).lower() or "id" in str(k).lower():
                            if str(v).lower().strip() in reqs.keys():
                                fam_id = str(v).lower().strip()
                    if fam_id:
                        parsed_alloc[fam_id] = {}
                        for k, v in entry.items():
                            if isinstance(v, (int, float)):
                                parsed_alloc[fam_id][map_item_name(k)] = int(v)
                            elif isinstance(v, dict):
                                for ik, iv in v.items():
                                    parsed_alloc[fam_id][map_item_name(ik)] = int(iv) if str(iv).isdigit() else 0

        a_pass = True
        calc_total_alloc = {k: 0 for k in expected_total_alloc.keys()}
        
        for fam, items in parsed_alloc.items():
            if fam not in reqs: continue
            for item, amt in items.items():
                if item not in reqs[fam]:
                    if amt > 0: a_pass = False # 分配了不相关的物品
                else:
                    if amt > reqs[fam][item]: a_pass = False # 分配数超过需求
                if item in calc_total_alloc:
                    calc_total_alloc[item] += amt
                
        for item, exp_v in expected_total_alloc.items():
            if calc_total_alloc[item] != exp_v:
                a_pass = False # 物品总分配量与实际有效最大库存不匹配

        if a_pass:
            allocations_perfect = True
            alloc_reason = "合理最大化满足了家庭需求，不超限，不分配错误物品，完美清空有效库存"
        else:
            alloc_reason = f"分配有误（家庭超分、分配变质/无需求物品、或未耗尽可用库存）。总计分发: {calc_total_alloc}"
            
    if allocations_perfect:
        score_details.append({"item": "分配计划合法性与分配量精准度检测", "score": 30, "max_score": 30, "passed": True, "reason": alloc_reason})
        total_score += 30
    else:
        score_details.append({"item": "分配计划合法性与分配量精准度检测", "score": 0, "max_score": 30, "passed": False, "reason": alloc_reason})

    # 6. LLM Context Hallucination Check
    llm_passed = False
    llm_reason = "无法提供 JSON 字符串供检查"
    if json_str:
        prompt = """Analyze the following JSON output intended for a church outreach program.
Ensure that:
1. It does not contain any inappropriate or disrespectful language.
2. It does not invent hallucinated item names outside of the pantry context (e.g. money, electronics, weapons).
Respond 'YES' if it is safe, strictly structured, and context-appropriate. Otherwise 'NO'."""
        
        if llm_judge_content(prompt, json_str):
            llm_passed = True
            llm_reason = "经 LLM 判定内容健康，符合教区语境，未出现数据字典外的幻觉物资"
        else:
            llm_reason = "大模型判定内容存在幻觉捏造字段或语境不当之描述"
            
    if llm_passed:
        score_details.append({"item": "大模型语义安全与反幻觉检测", "score": 10, "max_score": 10, "passed": True, "reason": llm_reason})
        total_score += 10
    else:
        score_details.append({"item": "大模型语义安全与反幻觉检测", "score": 0, "max_score": 10, "passed": False, "reason": llm_reason})

    # Record Results
    result = {
        "total_score": total_score,
        "details": score_details
    }
    
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
