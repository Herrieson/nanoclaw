import os
import pandas as pd
import random

def build_env():
    base_dir = "assets/data_437"
    os.makedirs(os.path.join(base_dir, "logs"), exist_ok=True)
    os.makedirs(os.path.join(base_dir, "scripts"), exist_ok=True)

    # 1. 生成打卡日志
    employees = [
        {"id": "EMP001", "name": "John Doe", "sick_days": 8, "wellness_points": 45}, # 抵扣4天，扣4天
        {"id": "EMP002", "name": "Jane Smith", "sick_days": 2, "wellness_points": 30}, # 抵扣2天，扣0天
        {"id": "EMP003", "name": "Bob Wilson", "sick_days": 10, "wellness_points": 80}, # 抵扣5天(上限)，扣5天
        {"id": "EMP004", "name": "Alice Brown", "sick_days": 0, "wellness_points": 10}, # 抵扣0天，扣0天
    ]
    
    log_content = "timestamp,emp_id,event_type,value\n"
    for emp in employees:
        log_content += f"2023-10-01,{emp['id']},SICK_LEAVE,{emp['sick_days']}\n"
        log_content += f"2023-10-01,{emp['id']},WELLNESS_POINTS,{emp['wellness_points']}\n"
    
    with open(os.path.join(base_dir, "logs/daily_punching.log"), "w") as f:
        f.write(log_content)

    # 2. 生成一个错误的脚本
    # 错误点：1. 没考虑5天上限；2. 整数除法导致积分计算错误；3. 逻辑反了
    buggy_script = """
import pandas as pd
import os

def calculate():
    log_path = 'logs/daily_punching.log'
    df = pd.read_csv(log_path)
    
    # 错误的逻辑：直接相减，没考虑10:1比例，也没上限
    report = []
    for emp_id in df['emp_id'].unique():
        emp_data = df[df['emp_id'] == emp_id]
        sick = emp_data[emp_data['event_type'] == 'SICK_LEAVE']['value'].iloc[0]
        points = emp_data[emp_data['event_type'] == 'WELLNESS_POINTS']['value'].iloc[0]
        
        # BUG: 这里逻辑是乱写的
        net_sick_days = sick - points  # 极其离谱的逻辑
        
        report.append({
            'emp_id': emp_id,
            'final_sick_deduction': max(0, net_sick_days)
        })
    
    pd.DataFrame(report).to_csv('wellness_severance_report.csv', index=False)

if __name__ == "__main__":
    calculate()
"""
    with open(os.path.join(base_dir, "scripts/calc_bonus.py"), "w") as f:
        f.write(buggy_script)

    # 3. 生成一个初始的错误报告
    bad_report = "emp_id,final_sick_deduction\nEMP001,0\nEMP002,0\nEMP003,0\nEMP004,0"
    with open(os.path.join(base_dir, "wellness_severance_report.csv"), "w") as f:
        f.write(bad_report)

if __name__ == "__main__":
    build_env()
