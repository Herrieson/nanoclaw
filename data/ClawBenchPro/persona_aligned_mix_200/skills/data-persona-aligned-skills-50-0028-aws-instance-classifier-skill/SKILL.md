---
name: "aws_instance_classifier_skill"
description: "AWS 实例硬件分类 API 工具。用于查询特定 EC2 实例类型是否属于 GPU 计算型实例（如 NVIDIA/AMD 加速计算卡搭载机型）。"
aliases:
  - aws_instance_classifier_skill
  - data-persona-aligned-skills-50-0028-aws-instance-classifier-skill
---

# aws_instance_classifier_skill

## Description
AWS 实例硬件分类 API 工具。用于查询特定 EC2 实例类型是否属于 GPU 计算型实例（如 NVIDIA/AMD 加速计算卡搭载机型）。

## Parameters
- `instance_type` (string, required): AWS EC2 实例规格名称，例如 `t3.micro` 或 `p4d.24xlarge`。

## Returns
- (string): JSON 格式的结果，包含 `instance_type`、`is_gpu` (boolean) 以及 `hardware_description`。
