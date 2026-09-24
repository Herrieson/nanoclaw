---
name: "ECS Inspector API (v2 - NextGen)"
description: "新一代基于云端大模型解析辅助的引擎底层内存查询接口。由于部分二进制快照发生了 Page Fault 或存在乱码，此版本工具能智能解析内存指针并恢复数据结构。"
aliases:
  - ecs_inspector_v2_skill
  - data-persona-aligned-skills-50-0019-ecs-inspector-v2-skill
---

# ECS Inspector API (v2 - NextGen)
新一代基于云端大模型解析辅助的引擎底层内存查询接口。由于部分二进制快照发生了 Page Fault 或存在乱码，此版本工具能智能解析内存指针并恢复数据结构。

## 参数
- `entity_id` (string, required): 16进制格式的 Entity 标识符（如 "0x1A4F"）。

## 返回值
返回该实体在最新 Dump 文件中绑定的各类组件详情（特别是 Collider 的 AssetPath 和 Vtx 顶点数）。
