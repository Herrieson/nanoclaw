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
    此函数为检测非结构化文本的统一接口
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

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    target_file = os.path.join(workspace, "hotfix", "version_pin.json")
    
    score = 0
    details = []

    # ========================================================
    # 结构与存在性探针 (代码确定性解析)
    # ========================================================
    
    # 1. 结果文件是否存在 (10 分)
    if os.path.exists(target_file):
        details.append({"item": "目标文件存在性检查", "score": 10, "max_score": 10, "passed": True, "reason": "hotfix/version_pin.json 已成功创建"})
        score += 10
    else:
        details.append({"item": "目标文件存在性检查", "score": 0, "max_score": 10, "passed": False, "reason": "未找到要求的 hotfix/version_pin.json"})

    # 2. JSON 格式合法性 (10 分)
    json_data = None
    if os.path.exists(target_file):
        try:
            with open(target_file, "r", encoding="utf-8") as f:
                json_data = json.load(f)
            details.append({"item": "JSON 格式解析检查", "score": 10, "max_score": 10, "passed": True, "reason": "文件符合标准 JSON 格式，可成功反序列化"})
            score += 10
        except Exception as e:
            details.append({"item": "JSON 格式解析检查", "score": 0, "max_score": 10, "passed": False, "reason": f"反序列化 JSON 失败: {str(e)}"})
    else:
        details.append({"item": "JSON 格式解析检查", "score": 0, "max_score": 10, "passed": False, "reason": "前置文件缺失，无法进行格式验证"})

    # 3. 字段规范与防幻觉检查 (10 分)
    if isinstance(json_data, dict):
        expected_keys = {"conflict_pkg", "bad_version", "system_version"}
        actual_keys = set(json_data.keys())
        if expected_keys.issubset(actual_keys):
            if len(actual_keys) == 3:
                details.append({"item": "必需字段与防幻觉检查", "score": 10, "max_score": 10, "passed": True, "reason": "包含所有关键业务字段，且无擅自捏造的多余字段"})
                score += 10
            else:
                extra = actual_keys - expected_keys
                details.append({"item": "必需字段与防幻觉检查", "score": 5, "max_score": 10, "passed": False, "reason": f"结构可用但带有多余捏造字段，如: {list(extra)}"})
                score += 5
        else:
            missing = expected_keys - actual_keys
            details.append({"item": "必需字段与防幻觉检查", "score": 0, "max_score": 10, "passed": False, "reason": f"缺失致命核心字段: {list(missing)}"})
    else:
        if json_data is not None:
            details.append({"item": "必需字段与防幻觉检查", "score": 0, "max_score": 10, "passed": False, "reason": "JSON 根节点非 dict 类型，无法提取字段"})
        else:
            details.append({"item": "必需字段与防幻觉检查", "score": 0, "max_score": 10, "passed": False, "reason": "JSON 解析失败，跳过字段验证"})

    # ========================================================
    # 核心业务逻辑精准度探针 (原生精准对比，严防正则漏洞)
    # ========================================================
    
    if isinstance(json_data, dict):
        # 4. conflict_pkg 精准提取 (20 分)
        val_pkg = str(json_data.get("conflict_pkg", "")).strip()
        if val_pkg == "core-boost-python-wheels":
            details.append({"item": "conflict_pkg 数据精准度", "score": 20, "max_score": 20, "passed": True, "reason": "精准锁定了引发冲突的内网 Python 包名"})
            score += 20
        else:
            details.append({"item": "conflict_pkg 数据精准度", "score": 0, "max_score": 20, "passed": False, "reason": f"跨文件关联错误或提取错误，预期为 'core-boost-python-wheels'，实际为 '{val_pkg}'"})

        # 5. bad_version 精准提取 (20 分)
        val_bad = str(json_data.get("bad_version", "")).strip()
        if val_bad == "1.81.0":
            details.append({"item": "bad_version 数据精准度", "score": 20, "max_score": 20, "passed": True, "reason": "准确抓取出由包带入的破坏性高版本号 (1.81.0)"})
            score += 20
        else:
            details.append({"item": "bad_version 数据精准度", "score": 0, "max_score": 20, "passed": False, "reason": f"错误版本号提取失败，实际找到的为 '{val_bad}'"})

        # 6. system_version 精准提取 (20 分)
        val_sys = str(json_data.get("system_version", "")).strip()
        if val_sys == "1.74.0":
            details.append({"item": "system_version 数据精准度", "score": 20, "max_score": 20, "passed": True, "reason": "准确抓取出系统底层基础镜像的预期版本号 (1.74.0)"})
            score += 20
        else:
            details.append({"item": "system_version 数据精准度", "score": 0, "max_score": 20, "passed": False, "reason": f"底座镜像版本号提取失败，实际为 '{val_sys}'"})
    else:
        details.append({"item": "conflict_pkg 数据精准度", "score": 0, "max_score": 20, "passed": False, "reason": "前置依赖失败，无法读取数据"})
        details.append({"item": "bad_version 数据精准度", "score": 0, "max_score": 20, "passed": False, "reason": "前置依赖失败，无法读取数据"})
        details.append({"item": "system_version 数据精准度", "score": 0, "max_score": 20, "passed": False, "reason": "前置依赖失败，无法读取数据"})

    # ========================================================
    # 行为约束与业务意图合规探针 (LLM 语义分析)
    # ========================================================
    
    # 7. 不输出冗余排查长篇大论指令遵从度 (10 分)
    hotfix_dir = os.path.join(workspace, "hotfix")
    extra_files = []
    if os.path.exists(hotfix_dir):
        for f in os.listdir(hotfix_dir):
            if f != "version_pin.json" and os.path.isfile(os.path.join(hotfix_dir, f)):
                extra_files.append(f)
    
    if not extra_files:
        details.append({"item": "Persona及业务指令合规度", "score": 10, "max_score": 10, "passed": True, "reason": "严格遵守'别扯排查思路'的指示，未在结果目录下生成任何多余的废话报告文件"})
        score += 10
    else:
        file_to_check = os.path.join(hotfix_dir, extra_files[0])
        try:
            with open(file_to_check, "r", encoding="utf-8") as f:
                content = f.read()[:2000]
            
            prompt = (
                "The system persona explicitly instructed: 'Don't give me troubleshooting logic, I have no time to read reports!'. "
                "Does this text contain extensive explanation, troubleshooting steps, logs, or excuses regarding the pipeline failure? "
            )
            is_violating = llm_judge_content(prompt, content)
            
            if is_violating:
                details.append({"item": "Persona及业务指令合规度", "score": 0, "max_score": 10, "passed": False, "reason": f"大模型裁判检测到严重违规：Agent 在 {extra_files[0]} 中留下了长篇大论的排查思路或借口，无视了时间紧迫的限制"})
            else:
                details.append({"item": "Persona及业务指令合规度", "score": 5, "max_score": 10, "passed": False, "reason": f"存在非预期多余文件 {extra_files[0]}，但经大模型判定并不包含严重的排查报告长文"})
                score += 5
        except Exception as e:
             details.append({"item": "Persona及业务指令合规度", "score": 0, "max_score": 10, "passed": False, "reason": f"尝试读取多余文件时发生错误: {str(e)}"})

    # ========================================================
    # 结果持久化
    # ========================================================
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump({"total_score": score, "details": details}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify()
