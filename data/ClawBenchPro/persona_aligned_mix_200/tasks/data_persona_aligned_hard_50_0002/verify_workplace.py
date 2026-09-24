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
    # 此函数为检测非结构化文本的统一接口（尽管本题主要是结构化校验，仍予以保留作为标准扩展层）
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

def verify_workspace(workspace_path):
    details = []
    total_score = 0
    
    # 目标路径
    report_dir = os.path.join(workspace_path, "ci_patch")
    report_file = os.path.join(report_dir, "conflict_report.json")
    
    # 1. 物理结构校验 (10分)
    if os.path.isdir(report_dir) and os.path.isfile(report_file):
        details.append({"item": "结构探针：检查输出目录与文件", "score": 10, "max_score": 10, "passed": True, "reason": "目标文件 ci_patch/conflict_report.json 存在。"})
        total_score += 10
    else:
        details.append({"item": "结构探针：检查输出目录与文件", "score": 0, "max_score": 10, "passed": False, "reason": "未找到要求的目录或文件 ci_patch/conflict_report.json。"})
        # 物理文件丢失直接写入得分并退出
        with open(os.path.join(workspace_path, "workplace_score.json"), "w", encoding="utf-8") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        return

    # 2. JSON 格式合法性解析 (10分)
    try:
        with open(report_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        details.append({"item": "格式探针：合法JSON结构验证", "score": 10, "max_score": 10, "passed": True, "reason": "文件是合法的 JSON，解析成功。"})
        total_score += 10
    except Exception as e:
        details.append({"item": "格式探针：合法JSON结构验证", "score": 0, "max_score": 10, "passed": False, "reason": f"文件格式损坏，JSON原生解析失败: {e}"})
        # 无法解析则中断
        with open(os.path.join(workspace_path, "workplace_score.json"), "w", encoding="utf-8") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        return

    # 3. 字段完整性与幻觉控制 (20分)
    # 严格校验是否只包含且只包含了那三个字段
    if not isinstance(data, dict):
        details.append({"item": "Schema探针：字段约束验证", "score": 0, "max_score": 20, "passed": False, "reason": "JSON根节点非对象类型。"})
    else:
        actual_keys = set(data.keys())
        expected_keys = {"package", "version_a", "version_b"}
        
        if actual_keys == expected_keys:
            details.append({"item": "Schema探针：字段约束验证", "score": 20, "max_score": 20, "passed": True, "reason": "完美匹配字段要求，无缺失也无多余的捏造字段。"})
            total_score += 20
        elif expected_keys.issubset(actual_keys):
            details.append({"item": "Schema探针：字段约束验证", "score": 5, "max_score": 20, "passed": False, "reason": f"存在核心字段，但捏造了多余字段 (存在幻觉): {actual_keys - expected_keys}"})
            total_score += 5
        else:
            details.append({"item": "Schema探针：字段约束验证", "score": 0, "max_score": 20, "passed": False, "reason": f"缺失核心字段。期望: {expected_keys}, 实际提取: {actual_keys}"})

    # 4. 数据探针：多跳逻辑包名校验 (30分)
    package_name = str(data.get("package", "")).strip()
    if package_name == "lib_eigen_tensor_v2":
        details.append({"item": "逻辑探针：真实依赖反查", "score": 30, "max_score": 30, "passed": True, "reason": "成功通过注册表哈希分片反查到唯一正确的脱敏包名。"})
        total_score += 30
    else:
        details.append({"item": "逻辑探针：真实依赖反查", "score": 0, "max_score": 30, "passed": False, "reason": f"真实依赖包名错误。提取值: '{package_name}'。"})

    # 5. 数据探针：确定性版本提取校验 (30分)
    va = str(data.get("version_a", "")).strip()
    vb = str(data.get("version_b", "")).strip()
    extracted_versions = {va, vb}
    expected_versions = {"3.3.9", "3.4.2"}
    
    if extracted_versions == expected_versions:
        details.append({"item": "逻辑探针：冲突版本数值提取", "score": 30, "max_score": 30, "passed": True, "reason": "无顺序干扰，精确提取到了 3.3.9 与 3.4.2 两个冲突版本。"})
        total_score += 30
    else:
        details.append({"item": "逻辑探针：冲突版本数值提取", "score": 0, "max_score": 30, "passed": False, "reason": f"冲突版本号提取错误。提取集合: {extracted_versions}。"})

    # 输出得分总览
    score_file = os.path.join(workspace_path, "workplace_score.json")
    with open(score_file, "w", encoding="utf-8") as f:
        json.dump({
            "total_score": total_score,
            "details": details
        }, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    work_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    verify_workspace(work_dir)
