import os
import sys
import json

def calculate_average_phred(qual_str):
    if not qual_str:
        return 0
    return sum(ord(c) - 33 for c in qual_str) / len(qual_str)

def get_gold_standard(fastq_path):
    adapter = "GATCGGAAGAGCACACGTC"
    surviving_ids = []
    
    if not os.path.exists(fastq_path):
        return surviving_ids

    with open(fastq_path, 'r') as f:
        while True:
            header = f.readline().strip()
            if not header:
                break
            seq = f.readline().strip()
            plus = f.readline().strip()
            qual = f.readline().strip()
            
            # 规则 1: 剔除包含接头的
            if adapter in seq:
                continue
            
            # 规则 2: 平均质量分数低于 20 的剔除
            if calculate_average_phred(qual) < 20:
                continue
            
            # 提取 ID (去除开头的 @)
            read_id = header[1:] if header.startswith('@') else header
            surviving_ids.append(read_id)
            
    return surviving_ids

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    fastq_path = os.path.join(workspace, "raw_data/run_774.fastq")
    result_path = os.path.join(workspace, "results/surviving_reads.txt")
    
    score = 0
    details = []

    # 1. 检查结果文件是否存在
    if os.path.exists(result_path):
        score += 10
        details.append({"item": "结果文件存在性", "score": 10, "max_score": 10, "passed": True, "reason": "results/surviving_reads.txt 已生成"})
    else:
        details.append({"item": "结果文件存在性", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 results/surviving_reads.txt"})
        # 如果文件不存在，后续检查无法进行
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": 0, "details": details}, f)
        return

    # 2. 读取并验证结果格式
    with open(result_path, 'r') as f:
        agent_lines = [line.strip() for line in f.readlines() if line.strip()]
    
    has_at_prefix = any(line.startswith('@') for line in agent_lines)
    if not has_at_prefix:
        score += 20
        details.append({"item": "输出格式正确性（无@前缀）", "score": 20, "max_score": 20, "passed": True, "reason": "Read ID 符合要求，没有包含 @ 符号"})
    else:
        details.append({"item": "输出格式正确性（无@前缀）", "score": 0, "max_score": 20, "passed": False, "reason": "部分 Read ID 仍保留了 FASTQ 的 @ 前缀"})

    # 3. 逻辑验证（金标准比对）
    gold_ids = set(get_gold_standard(fastq_path))
    agent_ids = set(agent_lines)
    
    # 计算交集、差集
    tp = len(gold_ids.intersection(agent_ids))
    fp = len(agent_ids - gold_ids)
    fn = len(gold_ids - agent_ids)
    
    if len(gold_ids) == 0:
        accuracy_score = 0 # 异常情况
    else:
        # 允许极小误差，但逻辑错误（如没过滤接头或质量分算错）会导致大量差异
        accuracy = tp / len(gold_ids) if len(gold_ids) > 0 else 0
        penalty = (fp / len(gold_ids)) * 0.5 # 错选惩罚
        
        final_acc_score = max(0, (accuracy - penalty) * 70)
        score += int(final_acc_score)
        
        if final_acc_score >= 65:
            details.append({"item": "数据过滤准确性", "score": int(final_acc_score), "max_score": 70, "passed": True, "reason": f"匹配率极高: 命中 {tp}, 多选 {fp}, 漏选 {fn}"})
        else:
            details.append({"item": "数据过滤准确性", "score": int(final_acc_score), "max_score": 70, "passed": False, "reason": f"过滤逻辑存在明显偏差: 命中 {tp}, 多选 {fp}, 漏选 {fn}"})

    # 总结输出
    final_score = min(100, score)
    output = {
        "total_score": int(final_score),
        "details": details
    }
    
    with open("workplace_score.json", "w") as f:
        json.dump(output, f, indent=2)

if __name__ == "__main__":
    main()
