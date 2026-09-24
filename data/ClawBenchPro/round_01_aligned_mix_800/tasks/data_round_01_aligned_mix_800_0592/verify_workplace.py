import os
import sys
import json
import yaml
import glob

def calculate_ground_truth(workspace):
    """
    根据 env_builder 的逻辑，在验证脚本内部重新计算理论正确值，
    以此作为锚点，而不需要在外部存储答案。
    """
    approved_sessions = set()
    total_billed_hours = 0.0
    expected_wav_files = []

    # 1. 找出所有 APPROVED 的 Session ID
    qc_root = os.path.join(workspace, "logs/quality_control")
    for root, _, files in os.walk(qc_root):
        for file in files:
            if file.endswith(".json"):
                try:
                    with open(os.path.join(root, file), 'r') as f:
                        data = json.load(f)
                        if data.get("status") == "APPROVED":
                            approved_sessions.add(data.get("session_id"))
                except:
                    continue

    # 2. 统计这些 Session 的 billed_hours
    invoice_root = os.path.join(workspace, "finance/invoices")
    for file in os.listdir(invoice_root):
        if file.endswith(".yaml"):
            try:
                with open(os.path.join(invoice_root, file), 'r') as f:
                    data = yaml.safe_load(f)
                    if data.get("session_id") in approved_sessions:
                        total_billed_hours += data.get("billed_hours", 0)
            except:
                continue

    # 3. 找出这些 Session 对应的 _final.wav
    audio_root = os.path.join(workspace, "audio_archive")
    for root, _, files in os.walk(audio_root):
        for file in files:
            if file.endswith("_final.wav"):
                # 检查文件名是否属于 approved_sessions
                # 格式通常为 SES-XXX_instrument_final.wav
                prefix = file.split("_")[0]
                if prefix in approved_sessions:
                    expected_wav_files.append(file)

    return approved_sessions, round(total_billed_hours, 2), sorted(expected_wav_files)

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    details = []

    target_dir = os.path.join(workspace, "ready_for_mix")
    summary_path = os.path.join(target_dir, "summary.json")

    # 计算真值
    approved_ids, true_hours, true_wavs = calculate_ground_truth(workspace)

    # 1. 检查目录和 summary.json 存在性 (10分)
    if os.path.exists(target_dir) and os.path.isdir(target_dir):
        score += 5
        details.append({"item": "目录 ready_for_mix 存在", "score": 5, "max_score": 5, "passed": True})
    else:
        details.append({"item": "目录 ready_for_mix 存在", "score": 0, "max_score": 5, "passed": False})

    if os.path.exists(summary_path):
        score += 5
        details.append({"item": "summary.json 存在", "score": 5, "max_score": 5, "passed": True})
    else:
        details.append({"item": "summary.json 存在", "score": 0, "max_score": 5, "passed": False})

    # 2. 验证 billed_hours 计算准确性 (30分)
    billed_hours_passed = False
    if os.path.exists(summary_path):
        try:
            with open(summary_path, 'r') as f:
                res_data = json.load(f)
            # 找到包含 hours 的 key
            found_hours = None
            for k, v in res_data.items():
                if isinstance(v, (int, float)) and abs(v - true_hours) < 0.1:
                    found_hours = v
                    break
            
            if found_hours is not None:
                score += 30
                billed_hours_passed = True
                details.append({"item": "总计计费时长验证", "score": 30, "max_score": 30, "passed": True, "reason": f"成功计算出正确时长: {true_hours}"})
            else:
                details.append({"item": "总计计费时长验证", "score": 0, "max_score": 30, "passed": False, "reason": f"时长计算错误，期望约 {true_hours}"})
        except Exception as e:
            details.append({"item": "总计计费时长验证", "score": 0, "max_score": 30, "passed": False, "reason": f"解析 summary.json 失败: {str(e)}"})

    # 3. 验证音频文件提取 (40分) - 梯度给分
    actual_wavs = [f for f in os.listdir(target_dir) if f.endswith(".wav")] if os.path.exists(target_dir) else []
    actual_wavs_sorted = sorted(actual_wavs)
    
    if len(true_wavs) > 0:
        correct_wavs = set(actual_wavs_sorted) & set(true_wavs)
        excess_wavs = set(actual_wavs_sorted) - set(true_wavs)
        
        # 计算召回率得分
        recall = len(correct_wavs) / len(true_wavs)
        wav_score = int(recall * 30) 
        
        # 如果存在多余文件（如把 take1 也复制进来了），扣除 10 分
        if len(excess_wavs) > 0:
            wav_score = max(0, wav_score - 10)
            reason = f"提取了 {len(correct_wavs)}/{len(true_wavs)} 个正确文件，但包含 {len(excess_wavs)} 个无关文件。"
        else:
            reason = f"成功提取 {len(correct_wavs)}/{len(true_wavs)} 个正确文件，无冗余。"
        
        score += wav_score
        details.append({"item": "音频文件提取与清洗 (wav)", "score": wav_score, "max_score": 40, "passed": recall > 0.9, "reason": reason})

    # 4. 验证 summary.json 中的文件列表 (20分)
    if os.path.exists(summary_path):
        try:
            with open(summary_path, 'r') as f:
                res_data = json.load(f)
            
            found_list = None
            for k, v in res_data.items():
                if isinstance(v, list) and len(v) > 0:
                    found_list = v
                    break
            
            if found_list and set(found_list) == set(true_wavs):
                score += 20
                details.append({"item": "summary.json 文件列表完整性", "score": 20, "max_score": 20, "passed": True})
            elif found_list:
                score += 10
                details.append({"item": "summary.json 文件列表完整性", "score": 10, "max_score": 20, "passed": False, "reason": "列表不完整或包含错误文件"})
            else:
                details.append({"item": "summary.json 文件列表完整性", "score": 0, "max_score": 20, "passed": False})
        except:
            details.append({"item": "summary.json 解析列表失败", "score": 0, "max_score": 20, "passed": False})

    # 最终分限制
    score = min(100, max(0, int(score)))
    
    # 输出结果
    output = {"total_score": score, "details": details}
    with open("workplace_score.json", "w") as f:
        json.dump(output, f, indent=4)

if __name__ == "__main__":
    verify()
