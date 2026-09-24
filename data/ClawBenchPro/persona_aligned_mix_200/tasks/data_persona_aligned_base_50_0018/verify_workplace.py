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

def get_ground_truth(workspace):
    """
    沙盒内探针自己执行硬核逻辑，重新解析数据计算 Ground Truth，避免假阴性/假阳性。
    """
    can_log = os.path.join(workspace, "chassis_can.log")
    radar_json = os.path.join(workspace, "sensor_data", "radar_track.json")
    
    if not os.path.exists(can_log) or not os.path.exists(radar_json):
        return set()
        
    aeb_timestamps = []
    with open(can_log, "r", encoding="utf-8") as f:
        for line in f:
            # 必须满足双重条件: 刹车CAN ID = 0x2B0, PAYLOAD 前两字节 = FF 01
            if "MSG_ID:0x2B0" in line and "PAYLOAD:[FF 01" in line:
                m = re.search(r"<(\d+)>", line)
                if m:
                    aeb_timestamps.append(int(m.group(1)))
                    
    truth_ids = set()
    with open(radar_json, "r", encoding="utf-8") as f:
        radar_data = json.load(f)
        
    frames = radar_data.get("data_stream", {}).get("radar_front_center", {}).get("frames", [])
    for frame in frames:
        stamp_ms = frame.get("header", {}).get("stamp_ms", 0)
        # 严密的时间戳对齐：雷达比底盘快 1500ms
        if (stamp_ms - 1500) in aeb_timestamps:
            objects = frame.get("payload", {}).get("tracked_entities", {}).get("radar_objects", [])
            for obj in objects:
                rcs = obj.get("attributes", {}).get("rcs_dbsm", 999.0)
                conf = obj.get("attributes", {}).get("track_confidence", 999)
                # 必须满足 rcs < 5.0 且 confidence < 60
                if rcs < 5.0 and conf < 60:
                    tid = obj.get("metadata", {}).get("track_id", "")
                    if tid:
                        truth_ids.add(tid)
                        
    return truth_ids

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    target_file = os.path.join(workspace, "analysis", "ghost_ids.json")
    
    details = []
    total_score = 0
    
    # 1. 验证目标文件存在性 (10分)
    if os.path.exists(target_file):
        total_score += 10
        details.append({"item": "检查目标文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件 analysis/ghost_ids.json 存在"})
    else:
        details.append({"item": "检查目标文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件 analysis/ghost_ids.json 不存在"})
        
    # 2. 验证结构纯净性 (20分)
    # 绝对禁止使用正则去匹配结构化结果，必须使用 json 库严格解析
    agent_ids = []
    is_valid_format = False
    if os.path.exists(target_file):
        try:
            with open(target_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list) and all(isinstance(i, str) for i in data):
                is_valid_format = True
                agent_ids = data
                total_score += 20
                details.append({"item": "JSON格式规范性验证", "score": 20, "max_score": 20, "passed": True, "reason": "是一个纯净的字符串数组"})
            else:
                details.append({"item": "JSON格式规范性验证", "score": 0, "max_score": 20, "passed": False, "reason": "结构错误，不是纯净的字符串数组"})
        except json.JSONDecodeError:
            details.append({"item": "JSON格式规范性验证", "score": 0, "max_score": 20, "passed": False, "reason": "非法的JSON文件"})
    else:
        details.append({"item": "JSON格式规范性验证", "score": 0, "max_score": 20, "passed": False, "reason": "文件缺失，无法验证"})

    # 3. 数据精准度 (70分)
    if is_valid_format:
        truth_ids = get_ground_truth(workspace)
        agent_set = set(agent_ids)
        
        if not truth_ids:
            # 如果极端情况环境加载异常，这里进行容错
            details.append({"item": "验证提取的 ID 准确性", "score": 0, "max_score": 70, "passed": False, "reason": "Ground Truth 数据生成错误，请检查环境"})
        else:
            intersection = agent_set.intersection(truth_ids)
            false_positives = agent_set - truth_ids
            false_negatives = truth_ids - agent_set
            
            union_len = len(agent_set.union(truth_ids))
            # 使用严格的 Jaccard 相似度来反映 F1 维度的惩罚机制，有捏造、漏报均会急剧降分
            data_score = int(70 * (len(intersection) / union_len)) if union_len > 0 else 0
            
            total_score += data_score
            passed = (data_score == 70)
            reason = f"精准度检查完成。正确提取: {len(intersection)}项, 漏报: {len(false_negatives)}项, 误报(幻觉/条件错误): {len(false_positives)}项"
            details.append({"item": "验证提取的 ID 准确性", "score": data_score, "max_score": 70, "passed": passed, "reason": reason})
    else:
        details.append({"item": "验证提取的 ID 准确性", "score": 0, "max_score": 70, "passed": False, "reason": "由于文件不存在或格式不合规，跳过数据校验"})

    # 统分写入
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump({
            "total_score": total_score,
            "details": details
        }, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
