import os
import sys
import json
import httpx
from openai import OpenAI

# 强制从环境变量读取 LLM 配置，符合防御性编程及 API 规范
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# 强制关闭 SSL 验证
http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def llm_judge_content(prompt_text, file_content):
    """
    LLM 统一判定接口，仅返回 True / False，用于非结构化语义验证。
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
    # 接收工作区路径，默认当前目录
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    
    score_details = []
    total_score = 0
    
    # -------------------------------------------------------------
    # 1. 验证目标目录结构 (10 分)
    # -------------------------------------------------------------
    deliverables_path = os.path.join(workspace, "deliverables")
    if os.path.isdir(deliverables_path):
        score_details.append({"item": "检查目标交付目录 deliverables 是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "成功创建 deliverables 目录"})
        total_score += 10
    else:
        score_details.append({"item": "检查目标交付目录 deliverables 是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 deliverables 目录"})

    # -------------------------------------------------------------
    # 2. 验证 missing_waivers.json (20 分)
    # 此文件内容来源于动态的 API (LLM mock)，因此代码验证其 JSON 合法性，
    # 并辅以 LLM 进行“语义和意图”检测，确保其能用作前端邮件系统的输入。
    # -------------------------------------------------------------
    mw_path = os.path.join(deliverables_path, "missing_waivers.json")
    if os.path.isfile(mw_path):
        try:
            with open(mw_path, 'r', encoding='utf-8') as f:
                mw_data = json.load(f)
            score_details.append({"item": "missing_waivers.json 结构合法性", "score": 10, "max_score": 10, "passed": True, "reason": "JSON 格式完全合法"})
            total_score += 10
            
            # 使用 LLM 检测语义：是否包含合理的乘客标识符以用于邮件发送
            mw_content_str = json.dumps(mw_data, indent=2)
            prompt = "The provided JSON content should represent a list or dictionary of tour passengers who are missing their environmental waivers. Is this JSON semantically clear for an automated email system, and does it realistically contain clear passenger identifiers (like ticket IDs T-880x or passenger names) without containing junk data?"
            
            if llm_judge_content(prompt, mw_content_str[:1000]):
                score_details.append({"item": "missing_waivers.json 语义可用性 (LLM 判定)", "score": 10, "max_score": 10, "passed": True, "reason": "LLM 判定此文件意图清晰，包含了乘客标识信息，可用作自动化邮件输入"})
                total_score += 10
            else:
                score_details.append({"item": "missing_waivers.json 语义可用性 (LLM 判定)", "score": 0, "max_score": 10, "passed": False, "reason": "LLM 判定此文件语义模糊、混杂无关数据或缺少合理的标识符"})

        except Exception as e:
            score_details.append({"item": "missing_waivers.json 结构合法性", "score": 0, "max_score": 10, "passed": False, "reason": f"无法解析为有效的 JSON: {e}"})
            score_details.append({"item": "missing_waivers.json 语义可用性 (LLM 判定)", "score": 0, "max_score": 10, "passed": False, "reason": "由于 JSON 损坏跳过语义验证"})
    else:
        score_details.append({"item": "missing_waivers.json 结构合法性", "score": 0, "max_score": 10, "passed": False, "reason": "文件 missing_waivers.json 丢失"})
        score_details.append({"item": "missing_waivers.json 语义可用性 (LLM 判定)", "score": 0, "max_score": 10, "passed": False, "reason": "文件丢失"})

    # -------------------------------------------------------------
    # 3. 验证 fixed_route.json (总计 70 分)
    # 此处要求极高的解析严格度，绝不允许正则匹配，直接验证 schema 与数值逻辑
    # -------------------------------------------------------------
    fr_path = os.path.join(deliverables_path, "fixed_route.json")
    if os.path.isfile(fr_path):
        try:
            with open(fr_path, 'r', encoding='utf-8') as f:
                fr_data = json.load(f)
            score_details.append({"item": "fixed_route.json 格式合法性", "score": 10, "max_score": 10, "passed": True, "reason": "JSON 格式完全合法"})
            total_score += 10
            
            # (1) 检查数组长度和完整性 (10分)
            if isinstance(fr_data, list) and len(fr_data) == 4:
                score_details.append({"item": "fixed_route.json 节点完整度检查", "score": 10, "max_score": 10, "passed": True, "reason": "包含恰好 4 个地标节点，未丢失数据"})
                total_score += 10
                
                # (2) 检查字段的移除与新增 (20分)
                keys_correct = True
                for item in fr_data:
                    # 严防幻觉与未处理数据: 必须剔除 geo_hash，必须包含 lat 和 lon
                    if 'geo_hash' in item or 'lat' not in item or 'lon' not in item:
                        keys_correct = False
                        break
                
                if keys_correct:
                    score_details.append({"item": "fixed_route.json Schema 替换检查", "score": 20, "max_score": 20, "passed": True, "reason": "已彻底剔除旧版 geo_hash 键，并成功注入 lat 与 lon 键"})
                    total_score += 20
                    
                    # (3) 核心考察: 倒置坐标的逻辑修复修正 (30分)
                    # Agent 应该将倒置的坐标（例如经度变为 39，纬度变为 -82）修正为北美坐标系（俄亥俄州应为 Lat~39, Lon~-82）。
                    coords_flipped_back = True
                    for item in fr_data:
                        try:
                            lat = float(item['lat'])
                            lon = float(item['lon'])
                            # 限定俄亥俄州合理容差范围: 纬度 35~45，经度 -90~-75
                            if not (35 <= lat <= 45) or not (-90 <= lon <= -75):
                                coords_flipped_back = False
                                break
                        except Exception:
                            coords_flipped_back = False
                            break
                    
                    if coords_flipped_back:
                        score_details.append({"item": "fixed_route.json 核心逻辑：倒置坐标清洗修正", "score": 30, "max_score": 30, "passed": True, "reason": "成功将解码器返回的反转坐标进行清洗对调，所有坐标已重置回合理的北美范围 (Lat ~39, Lon ~-82)"})
                        total_score += 30
                    else:
                        score_details.append({"item": "fixed_route.json 核心逻辑：倒置坐标清洗修正", "score": 0, "max_score": 30, "passed": False, "reason": "坐标数据仍在南极甚至非法格式，Agent 盲目转存了反转的数据，未执行纠错替换逻辑"})
                else:
                    score_details.append({"item": "fixed_route.json Schema 替换检查", "score": 0, "max_score": 20, "passed": False, "reason": "Schema 错误: 仍残留 geo_hash 或丢失 lat/lon，拒绝得分"})
                    score_details.append({"item": "fixed_route.json 核心逻辑：倒置坐标清洗修正", "score": 0, "max_score": 30, "passed": False, "reason": "前置 Schema 错误导致逻辑验证无法进行"})
            else:
                score_details.append({"item": "fixed_route.json 节点完整度检查", "score": 0, "max_score": 10, "passed": False, "reason": "数据结构不是数组或节点数量不是 4，发生数据截断或捏造"})
                score_details.append({"item": "fixed_route.json Schema 替换检查", "score": 0, "max_score": 20, "passed": False, "reason": "前置错误"})
                score_details.append({"item": "fixed_route.json 核心逻辑：倒置坐标清洗修正", "score": 0, "max_score": 30, "passed": False, "reason": "前置错误"})
                
        except Exception as e:
            score_details.append({"item": "fixed_route.json 格式合法性", "score": 0, "max_score": 10, "passed": False, "reason": f"无法解析为有效的 JSON: {e}"})
            score_details.append({"item": "fixed_route.json 节点完整度检查", "score": 0, "max_score": 10, "passed": False, "reason": "跳过"})
            score_details.append({"item": "fixed_route.json Schema 替换检查", "score": 0, "max_score": 20, "passed": False, "reason": "跳过"})
            score_details.append({"item": "fixed_route.json 核心逻辑：倒置坐标清洗修正", "score": 0, "max_score": 30, "passed": False, "reason": "跳过"})
    else:
        score_details.append({"item": "fixed_route.json 格式合法性", "score": 0, "max_score": 10, "passed": False, "reason": "文件 fixed_route.json 丢失"})
        score_details.append({"item": "fixed_route.json 节点完整度检查", "score": 0, "max_score": 10, "passed": False, "reason": "缺失"})
        score_details.append({"item": "fixed_route.json Schema 替换检查", "score": 0, "max_score": 20, "passed": False, "reason": "缺失"})
        score_details.append({"item": "fixed_route.json 核心逻辑：倒置坐标清洗修正", "score": 0, "max_score": 30, "passed": False, "reason": "缺失"})

    # 4. 汇总写入报告
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump({
            "total_score": total_score,
            "details": score_details
        }, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify()
