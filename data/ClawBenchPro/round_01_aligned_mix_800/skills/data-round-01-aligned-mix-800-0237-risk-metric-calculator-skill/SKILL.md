---
name: "Risk Metric Calculator Skill"
description: "用于计算社工案例的“综合风险指数”。"
aliases:
  - risk_metric_calculator_skill
  - data-round-01-aligned-mix-800-0237-risk-metric-calculator-skill
---

# Risk Metric Calculator Skill

用于计算社工案例的“综合风险指数”。

## 输入参数
- `score`: int, 原始评估分数 (0-100)
- `transcript`: str, 家访记录转录文本

## 输出
- `risk_index`: float (0.0 - 1.0), 数值越高表示风险越大。
