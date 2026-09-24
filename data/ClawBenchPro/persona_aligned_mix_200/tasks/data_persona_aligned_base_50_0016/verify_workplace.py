import os
import sys
import json
import re
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
    target_file = os.path.join(workspace, "processed", "clean_traj_ids.txt")
    
    score_details = []
    total_score = 0
    
    # 1. 检查目标文件是否存在 (15分)
    file_exists = os.path.exists(target_file) and os.path.isfile(target_file)
    if file_exists:
        score_details.append({"item": "检查目标文件是否存在", "score": 15, "max_score": 15, "passed": True, "reason": "成功找到 `processed/clean_traj_ids.txt`"})
        total_score += 15
    else:
        score_details.append({"item": "检查目标文件是否存在", "score": 0, "max_score": 15, "passed": False, "reason": "未找到目标文件 `processed/clean_traj_ids.txt`"})
        
    extracted_ids = []
    pure_format = False
    
    if file_exists:
        try:
            with open(target_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            # 清理空行并解析
            raw_lines = [line.strip() for line in lines if line.strip()]
            
            # 2. 检查输出纯净度 (10分)
            # 要求：别整那些没用的报告，只要 ID。所有的非空行应当全都是形如 T-xxxx 的格式。
            pure_format = all(re.match(r'^T-\d+$', line) for line in raw_lines)
            if pure_format and len(raw_lines) > 0:
                score_details.append({"item": "检查输出纯净度", "score": 10, "max_score": 10, "passed": True, "reason": "输出无冗余报告废话，每行格式均为合法的 ID"})
                total_score += 10
            else:
                score_details.append({"item": "检查输出纯净度", "score": 0, "max_score": 10, "passed": False, "reason": "输出中混杂了自然语言报告、无效格式或文件全空"})
            
            # 尝试提取出里面看起来像ID的串用于进一步逻辑验证
            extracted_ids = []
            for line in raw_lines:
                # 若包含自然语言，则利用正则从中强行提取 T-xxx 评估实质清洗逻辑
                matches = re.findall(r'T-\d+', line)
                extracted_ids.extend(matches)
                
        except Exception as e:
            score_details.append({"item": "检查输出纯净度", "score": 0, "max_score": 10, "passed": False, "reason": f"文件读取异常: {e}"})
    else:
        score_details.append({"item": "检查输出纯净度", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在，跳过纯净度检查"})

    extracted_set = set(extracted_ids)

    # 3. 检查乱码与损坏数据过滤能力 (15分)
    # T-1005 (json未闭合) 和 T-1006 (十六进制乱码前缀) 不应存在
    if file_exists:
        if "T-1005" not in extracted_set and "T-1006" not in extracted_set:
            score_details.append({"item": "过滤损坏的JSON与乱码数据", "score": 15, "max_score": 15, "passed": True, "reason": "正确剔除了无法被正常解析的 T-1005 和 T-1006"})
            total_score += 15
        else:
            score_details.append({"item": "过滤损坏的JSON与乱码数据", "score": 0, "max_score": 15, "passed": False, "reason": "未正确拦截格式残缺或含乱码前缀的脏数据"})
    else:
         score_details.append({"item": "过滤损坏的JSON与乱码数据", "score": 0, "max_score": 15, "passed": False, "reason": "文件不存在，该项记 0 分"})

    # 4. 检查 Token 截断数据的过滤能力 (15分)
    # T-1003 (finish_reason = length) 不应存在
    if file_exists:
        if "T-1003" not in extracted_set:
            score_details.append({"item": "过滤严重截断数据", "score": 15, "max_score": 15, "passed": True, "reason": "正确剔除了因为 max_tokens 截断（length）的残缺数据 T-1003"})
            total_score += 15
        else:
            score_details.append({"item": "过滤严重截断数据", "score": 0, "max_score": 15, "passed": False, "reason": "未正确拦截 finish_reason 为 length 的数据"})
    else:
         score_details.append({"item": "过滤严重截断数据", "score": 0, "max_score": 15, "passed": False, "reason": "文件不存在，该项记 0 分"})

    # 5. 检查 Agent 死循环数据的过滤能力 (15分)
    # T-1002 (连续相同的 tool calls) 不应存在
    if file_exists:
        if "T-1002" not in extracted_set:
            score_details.append({"item": "过滤陷入死循环的工具调用数据", "score": 15, "max_score": 15, "passed": True, "reason": "正确剔除了陷入无意义重复调用的 T-1002 数据"})
            total_score += 15
        else:
            score_details.append({"item": "过滤陷入死循环的工具调用数据", "score": 0, "max_score": 15, "passed": False, "reason": "未正确拦截呈现死循环特征的轨迹数据 T-1002"})
    else:
         score_details.append({"item": "过滤陷入死循环的工具调用数据", "score": 0, "max_score": 15, "passed": False, "reason": "文件不存在，该项记 0 分"})

    # 6. 检查健康轨迹的全量留存与拒答幻觉情况 (30分)
    # 正确的数据集应当只包含：T-1001, T-1004, T-1007
    if file_exists:
        expected_ids = {"T-1001", "T-1004", "T-1007"}
        missing_ids = expected_ids - extracted_set
        # 计算提取列表中多出的且不在剔除名单里的虚构 ID (幻觉)
        dirty_ids = {"T-1002", "T-1003", "T-1005", "T-1006"}
        hallucinated_ids = extracted_set - expected_ids - dirty_ids
        
        health_score = 30
        penalties = []
        
        if len(missing_ids) > 0:
            penalty = len(missing_ids) * 10
            health_score -= penalty
            penalties.append(f"遗漏了合法数据 {missing_ids}，扣 {penalty} 分")
            
        if len(hallucinated_ids) > 0:
            penalty = len(hallucinated_ids) * 10
            health_score -= penalty
            penalties.append(f"捏造了不存在的数据 ID {hallucinated_ids}，扣 {penalty} 分")
            
        health_score = max(0, health_score)
        
        if health_score == 30:
            score_details.append({"item": "精准留存合法数据与幻觉抑制", "score": 30, "max_score": 30, "passed": True, "reason": "完美找出了所有的健康数据 T-1001, T-1004, T-1007，且无捏造或多余数据！"})
        else:
            score_details.append({"item": "精准留存合法数据与幻觉抑制", "score": health_score, "max_score": 30, "passed": False, "reason": "; ".join(penalties)})
            
        total_score += health_score
    else:
         score_details.append({"item": "精准留存合法数据与幻觉抑制", "score": 0, "max_score": 30, "passed": False, "reason": "文件不存在，该项记 0 分"})

    # 保存评分文件
    score_data = {
        "total_score": total_score,
        "details": score_details
    }
    
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(score_data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    verify()
