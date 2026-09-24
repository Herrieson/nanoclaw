---
name: "ECS Inspector API (v1 - Legacy)"
description: "旧版底层内存查询接口。根据 Entity ID 查询对应实体在内存快照中绑定的各项组件数据（特别是 Collider/RigidBody 组件数据）。"
aliases:
  - ecs_inspector_v1_skill
  - data-persona-aligned-skills-50-0019-ecs-inspector-v1-skill
---

# ECS Inspector API (v1 - Legacy)
旧版底层内存查询接口。根据 Entity ID 查询对应实体在内存快照中绑定的各项组件数据（特别是 Collider/RigidBody 组件数据）。

## 参数
- `entity_id` (string, required): 16进制格式的 Entity 标识符（如 "0x1A4F"）。

## 返回值
该实体绑定的物理与网格组件内存映射结构。
