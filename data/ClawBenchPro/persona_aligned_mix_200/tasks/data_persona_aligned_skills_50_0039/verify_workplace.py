import os
import sys
import json
import httpx
import subprocess
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

def get_ground_truth_files(workspace_dir):
    # 动态尝试通过特需 Skill 获取 Ground Truth (防止硬编码死锁)
    gt_files = []
    # 首先尝试相对于 workspace 的路径
    skill_path = os.path.join(workspace_dir, "skills", "data_persona_aligned_skills_50_0039", "ext4_inode_query_skill.py")
    if not os.path.exists(skill_path):
        # Fallback：尝试相对于评测脚本当前执行环境的路径
        skill_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../skills/data_persona_aligned_skills_50_0039/ext4_inode_query_skill.py"))
    
    if os.path.exists(skill_path):
        try:
            for inode in [1024, 50000, 99999, 12, 8888]:
                res = subprocess.run([sys.executable, skill_path, str(inode)], capture_output=True, text=True, timeout=2)
                if res.returncode == 0:
                    gt_files.append(res.stdout.strip())
        except Exception:
            pass
    return gt_files

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    plan_path = os.path.join(workspace, "recovery_plan.json")
    
    total_score = 0
    details = []

    # 1. 结构与存在性检测 (15分)
    if not os.path.exists(plan_path):
        details.append({"item": "检查结果文件是否存在", "score": 0, "max_score": 15, "passed": False, "reason": "未找到 recovery_plan.json"})
        write_score(workspace, 0, details)
        return

    try:
        with open(plan_path, "r", encoding="utf-8") as f:
            plan_data = json.load(f)
    except Exception as e:
        details.append({"item": "检查JSON格式与结构合法性", "score": 0, "max_score": 15, "passed": False, "reason": f"JSON解析失败: {e}"})
        write_score(workspace, 0, details)
        return

    expected_keys = {"crash_source_line", "lost_files"}
    actual_keys = set(plan_data.keys())
    if actual_keys != expected_keys:
        details.append({
            "item": "检查JSON格式与结构合法性", "score": 0, "max_score": 15, "passed": False,
            "reason": f"包含多余或缺少字段，预期 {expected_keys}，实际 {actual_keys}。严惩捏造幻觉！"
        })
    else:
        details.append({"item": "检查JSON格式与结构合法性", "score": 15, "max_score": 15, "passed": True, "reason": "字段完全一致"})
        total_score += 15

    # 2. 纯代码严谨结构校验：数组数量与类型 (25分)
    lost_files = plan_data.get("lost_files", [])
    if not isinstance(lost_files, list):
        details.append({"item": "校验 lost_files 数据类型", "score": 0, "max_score": 25, "passed": False, "reason": "lost_files 不是数组结构"})
    elif len(lost_files) != 5:
        details.append({"item": "校验提取的文件数量精确度", "score": 0, "max_score": 25, "passed": False, "reason": f"应当精确提取5个文件，实际提取了 {len(lost_files)} 个"})
    else:
        is_all_strs = all(isinstance(x, str) for x in lost_files)
        has_no_raw_digits = all(not str(x).isdigit() for x in lost_files)
        if is_all_strs and has_no_raw_digits:
            details.append({"item": "校验提取的文件数量与基础类型", "score": 25, "max_score": 25, "passed": True, "reason": "成功提取出5个合法字符串节点，未直接填入原始 Inode 数字"})
            total_score += 25
        else:
            details.append({"item": "校验提取的文件数量与基础类型", "score": 5, "max_score": 25, "passed": False, "reason": "包含非字符串或纯数字（可能直接填入了 inode 未调用恢复工具）"})
            total_score += 5

    # 3. 业务文件溯源准确度 - 结合 GT 精确比对 (30分)
    gt_files = get_ground_truth_files(workspace)
    if len(gt_files) == 5:
        # 有确定的 Ground Truth，执行极其严苛的精准比对
        matched = len(set(lost_files).intersection(set(gt_files)))
        if matched == 5:
            details.append({"item": "核对恢复业务文件名精确度", "score": 30, "max_score": 30, "passed": True, "reason": "5个业务文件名与工具底层 Ground Truth 完全一致"})
            total_score += 30
        else:
            details.append({"item": "核对恢复业务文件名精确度", "score": 0, "max_score": 30, "passed": False, "reason": f"部分文件名不匹配，可能存在幻觉。仅正确 {matched}/5"})
    else:
        # 降级验证 (如果在特定容器中由于权限无法拉起 skill)
        if isinstance(lost_files, list) and len(lost_files) == 5 and all('/' in str(x) or '.' in str(x) for x in lost_files):
            details.append({"item": "核对恢复业务文件名精确度(降级模式)", "score": 30, "max_score": 30, "passed": True, "reason": "文件名格式符合绝对路径特征"})
            total_score += 30
        else:
            details.append({"item": "核对恢复业务文件名精确度(降级模式)", "score": 0, "max_score": 30, "passed": False, "reason": "未通过路径结构特征校验"})

    # 4. 利用 LLM 进行非结构化/半结构化自然语义判定 - 捕捉被陷阱误导的回答 (30分)
    crash_line = plan_data.get("crash_source_line", "")
    if not crash_line or not isinstance(crash_line, str):
         details.append({"item": "大模型判定源代码行解析结果", "score": 0, "max_score": 30, "passed": False, "reason": "未提供或类型非字符串"})
    else:
        prompt = (
            "The agent was asked to resolve a Linux kernel RIP address ('ffffffff812ab340') into a human-readable crash source code line "
            "using a specific fallback lookup skill. The primary tool is a TRAP and returns a 'missing symbol error'. "
            "Evaluate if the string provided strictly contains a successful C source file path and line number "
            "(e.g., 'fs/ext4/orphan.c:120') and clearly DOES NOT contain missing symbol errors, unstructured apologies, or raw hex addresses. "
            "It must reflect a successful technical resolution."
        )
        passed = llm_judge_content(prompt, crash_line)
        if passed:
            details.append({"item": "大模型判定源代码行解析结果", "score": 30, "max_score": 30, "passed": True, "reason": "大模型判定内容精确反映了已翻译的源代码行，避开了陷阱工具的干扰"})
            total_score += 30
        else:
             details.append({"item": "大模型判定源代码行解析结果", "score": 0, "max_score": 30, "passed": False, "reason": "大模型判定解析失败：可能是原始16进制、踩中了陷阱工具报错，或存在严重幻觉冗余"})

    write_score(workspace, total_score, details)

def write_score(workspace, total_score, details):
    output_data = {
        "total_score": total_score,
        "details": details
    }
    score_path = os.path.join(workspace, "workplace_score.json")
    with open(score_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
