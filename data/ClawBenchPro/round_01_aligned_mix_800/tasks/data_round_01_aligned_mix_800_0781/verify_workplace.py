import os
import sys
import json
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# 初始化客户端，必须关闭 SSL 验证
http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def llm_judge_content(prompt_text, file_content):
    """
    非结构化文本的 LLM 验证接口
    用于在此严格的结构化验证中，容错并判定附加的非结构化留言
    """
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

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0
    
    # 1. 检查目标目录 craft_plans 是否建立
    dir_path = os.path.join(workspace, "craft_plans")
    if os.path.isdir(dir_path):
        score_details.append({"item": "检查 craft_plans 目录是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "已正确创建存放规划的目录"})
        total_score += 10
    else:
        score_details.append({"item": "检查 craft_plans 目录是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 craft_plans 目录"})

    # 2. 检查结果文件 clean_inventory.json
    file_path = os.path.join(workspace, "craft_plans", "clean_inventory.json")
    data = None
    if os.path.isfile(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            score_details.append({"item": "检查 clean_inventory.json 是否存在且为有效 JSON", "score": 20, "max_score": 20, "passed": True, "reason": "文件存在且格式完全合法"})
            total_score += 20
        except Exception as e:
            score_details.append({"item": "检查 clean_inventory.json 是否存在且为有效 JSON", "score": 5, "max_score": 20, "passed": False, "reason": f"文件存在但非有效 JSON, 错误信息: {e}"})
            total_score += 5
    else:
        score_details.append({"item": "检查 clean_inventory.json 是否存在且为有效 JSON", "score": 0, "max_score": 20, "passed": False, "reason": "文件缺失，无法进行后续检查"})

    # 3. 解析与核心验证 (仅在成功读取顶层为字典的 JSON 后进行)
    if isinstance(data, dict):
        # 宽容提取数值（兼容首字母大小写或字符串类型的浮点数）
        clean_data = {}
        for k, v in data.items():
            clean_k = str(k).strip().lower()
            try:
                clean_data[clean_k] = float(v)
            except:
                pass
                
        required_keys = ['wood', 'fabric', 'glass']
        found_keys = [k for k in required_keys if k in clean_data]
        
        # 3.1 是否全部包含必需的类别
        if len(found_keys) == 3:
            score_details.append({"item": "检查 JSON 中是否包含三大必要类别", "score": 20, "max_score": 20, "passed": True, "reason": "包含了 Wood, Fabric, Glass 三大类"})
            total_score += 20
        else:
            score_details.append({"item": "检查 JSON 中是否包含三大必要类别", "score": len(found_keys) * 6, "max_score": 20, "passed": False, "reason": f"仅找到类别: {found_keys}，未满足全覆盖"})
            total_score += len(found_keys) * 6
            
        # 3.2 检查数据准确度 (Wood)
        if 'wood' in clean_data and abs(clean_data['wood'] - 25.5) < 0.01:
            score_details.append({"item": "检查 Wood 类的总重量准确度 (CSV + JSON合并)", "score": 15, "max_score": 15, "passed": True, "reason": "Wood 类的重量计算完全正确 (25.5)"})
            total_score += 15
        else:
            actual_val = clean_data.get('wood', '未找到')
            score_details.append({"item": "检查 Wood 类的总重量准确度 (CSV + JSON合并)", "score": 0, "max_score": 15, "passed": False, "reason": f"Wood 重量计算错误，期望: 25.5, 实际: {actual_val}"})
            
        # 3.3 检查数据准确度 (Fabric)
        if 'fabric' in clean_data and abs(clean_data['fabric'] - 12.0) < 0.01:
            score_details.append({"item": "检查 Fabric 类的总重量准确度 (CSV + JSON合并)", "score": 15, "max_score": 15, "passed": True, "reason": "Fabric 类的重量计算完全正确 (12.0)"})
            total_score += 15
        else:
            actual_val = clean_data.get('fabric', '未找到')
            score_details.append({"item": "检查 Fabric 类的总重量准确度 (CSV + JSON合并)", "score": 0, "max_score": 15, "passed": False, "reason": f"Fabric 重量计算错误，期望: 12.0, 实际: {actual_val}"})
            
        # 3.4 检查数据准确度 (Glass)
        if 'glass' in clean_data and abs(clean_data['glass'] - 5.5) < 0.01:
            score_details.append({"item": "检查 Glass 类的总重量准确度", "score": 10, "max_score": 10, "passed": True, "reason": "Glass 类的重量计算完全正确 (5.5)"})
            total_score += 10
        else:
            actual_val = clean_data.get('glass', '未找到')
            score_details.append({"item": "检查 Glass 类的总重量准确度", "score": 0, "max_score": 10, "passed": False, "reason": f"Glass 重量计算错误，期望: 5.5, 实际: {actual_val}"})

        # 3.5 严格的幻觉及有毒物质混入排查 (LLM 联合检查)
        extra_keys = [k for k in data.keys() if str(k).strip().lower() not in required_keys]
        if not extra_keys:
            score_details.append({"item": "检查多余内容与有毒物质是否已严格剔除", "score": 10, "max_score": 10, "passed": True, "reason": "干净纯粹，无任何多余结构或有毒物质保留"})
            total_score += 10
        else:
            # 首先排查有毒物硬伤
            toxic_found = False
            for k in extra_keys:
                k_str = str(k).lower()
                v_str = str(data[k]).lower()
                if any(bad in k_str or bad in v_str for bad in ['styrofoam', 'pvc', 'lead']):
                    toxic_found = True
                    break
            
            if toxic_found:
                score_details.append({"item": "检查多余内容与有毒物质是否已严格剔除", "score": 0, "max_score": 10, "passed": False, "reason": f"严重违背指令：提取物中混入了禁止的有毒类别 (如 styrofoam, pvc, lead)！冗余键：{extra_keys}"})
            else:
                # Agent 可能会好心留下诸如 {"Message": "Everything is safe now!"} 的非技术字段，需 LLM 判定
                extra_str = json.dumps({k: data[k] for k in extra_keys}, ensure_ascii=False)
                is_polite = llm_judge_content(
                    "Does the following JSON content contain ONLY comforting, polite, and reassuring words for an anxious mother? It MUST NOT contain any technical data, file IDs, toxic material names, or raw material lists. If it has ANY technical data, answer NO. If it is purely a polite message, answer YES.", 
                    extra_str
                )
                if is_polite:
                    score_details.append({"item": "检查多余内容与有毒物质是否已严格剔除", "score": 5, "max_score": 10, "passed": False, "reason": f"虽含有无关的多余字段，但被判定为抚慰用户的礼貌用语，扣除严格规范分5分: {extra_keys}"})
                    total_score += 5
                else:
                    score_details.append({"item": "检查多余内容与有毒物质是否已严格剔除", "score": 0, "max_score": 10, "passed": False, "reason": f"发现不相关的冗余字段，且不符合单纯抚慰的语气标准，污染了数据文件。字段: {extra_keys}"})
    else:
        # 如果文件无法解析或格式不匹配，剩余分数为 0
        if data is not None:
            score_details.append({"item": "JSON 结构有效性校验", "score": 0, "max_score": 20, "passed": False, "reason": "根节点并非对象/字典结构"})
        
        missed_items = [
            ("检查 JSON 中是否包含三大必要类别", 20),
            ("检查 Wood 类的总重量准确度 (CSV + JSON合并)", 15),
            ("检查 Fabric 类的总重量准确度 (CSV + JSON合并)", 15),
            ("检查 Glass 类的总重量准确度", 10),
            ("检查多余内容与有毒物质是否已严格剔除", 10)
        ]
        for item, max_s in missed_items:
            score_details.append({"item": item, "score": 0, "max_score": max_s, "passed": False, "reason": "由于前置 JSON 文件解析失败，此项直接判定得 0 分"})

    result = {
        "total_score": total_score,
        "details": score_details
    }
    
    with open(os.path.join(workspace, "workplace_score.json"), 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)
        
if __name__ == '__main__':
    main()
