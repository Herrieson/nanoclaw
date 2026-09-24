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
    # 此函数为检测非结构化文本的统一接口
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

def verify_workplace(workspace):
    score = 0
    details = []
    
    # 目标路径配置
    target_dir = os.path.join(workspace, "pipeline_fixes")
    target_file = os.path.join(target_dir, "patch.json")
    
    # 真实数据源（防止基于大模型的幻觉或模糊匹配，必须通过精准代码强校验）
    truth_node = "SHD_Flesh_Subsurface_09"
    truth_texture = "/prod/show/SC043/assets/chars/mutant/tex/v003/diffuse_UDIM_1001.tx"
    
    # 1. 验证目标目录是否存在 (10分)
    if os.path.isdir(target_dir):
        score += 10
        details.append({"item": "检查 pipeline_fixes 目录是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "成功创建 pipeline_fixes 目录"})
    else:
        details.append({"item": "检查 pipeline_fixes 目录是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 pipeline_fixes 目录"})
        
    # 2. 验证热修复文件是否存在 (10分)
    file_exists = os.path.isfile(target_file)
    if file_exists:
        score += 10
        details.append({"item": "检查 patch.json 文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "成功找到 patch.json 文件"})
    else:
        details.append({"item": "检查 patch.json 文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 patch.json 文件"})
        
    # 3. 严格验证 JSON 格式合法性及 Schema 字段约束 (20分)
    data = None
    if file_exists:
        try:
            with open(target_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # 使用强代码检查，严查任何画蛇添足的解释字段
            if isinstance(data, dict):
                keys = set(data.keys())
                expected_keys = {"broken_node", "missing_texture"}
                if keys == expected_keys:
                    score += 20
                    details.append({"item": "检查 JSON 格式与 Schema 合法性", "score": 20, "max_score": 20, "passed": True, "reason": "JSON 解析成功，且仅包含题目严格约束的两个字段，无冗余内容"})
                else:
                    details.append({"item": "检查 JSON 格式与 Schema 合法性", "score": 0, "max_score": 20, "passed": False, "reason": f"格式违规：包含预期外的字段或缺失字段，当前键集合：{list(keys)}"})
            else:
                details.append({"item": "检查 JSON 格式与 Schema 合法性", "score": 0, "max_score": 20, "passed": False, "reason": "JSON 根节点非字典(Object)类型"})
        except json.JSONDecodeError:
            details.append({"item": "检查 JSON 格式与 Schema 合法性", "score": 0, "max_score": 20, "passed": False, "reason": "文件不是合法的 JSON 格式，无法解析"})
    else:
        details.append({"item": "检查 JSON 格式与 Schema 合法性", "score": 0, "max_score": 20, "passed": False, "reason": "因文件不存在，无法进行格式校验"})

    # 4. 验证核心数据：故障节点名的精准提取 (30分)
    if data and isinstance(data, dict):
        node_val = data.get("broken_node", "")
        if node_val == truth_node:
            score += 30
            details.append({"item": "校验 broken_node 提取准确度", "score": 30, "max_score": 30, "passed": True, "reason": "成功在海量渲染日志的栈转储与十六进制报错中提取出真正的崩溃节点名"})
        else:
            details.append({"item": "校验 broken_node 提取准确度", "score": 0, "max_score": 30, "passed": False, "reason": f"节点提取错误，期望 [{truth_node}]，实际得到 [{node_val}]"})
            
    # 5. 验证核心数据：丢失贴图路径的精准解析与追踪 (30分)
    if data and isinstance(data, dict):
        tex_val = data.get("missing_texture", "")
        if tex_val == truth_texture:
            score += 30
            details.append({"item": "校验 missing_texture 提取准确度", "score": 30, "max_score": 30, "passed": True, "reason": "成功在深层嵌套(拓扑极度复杂)的场景树中穿透干扰项，定位到了关联的贴图绝对路径"})
        else:
            details.append({"item": "校验 missing_texture 提取准确度", "score": 0, "max_score": 30, "passed": False, "reason": f"贴图路径追踪失败，期望 [{truth_texture}]，实际得到 [{tex_val}]"})
    
    if not data or not isinstance(data, dict):
        details.append({"item": "校验 broken_node 提取准确度", "score": 0, "max_score": 30, "passed": False, "reason": "JSON 结构无效，无法校验提取准确度"})
        details.append({"item": "校验 missing_texture 提取准确度", "score": 0, "max_score": 30, "passed": False, "reason": "JSON 结构无效，无法校验提取准确度"})
        
    result = {
        "total_score": score,
        "details": details
    }
    
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    workspace_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    verify_workplace(workspace_dir)
