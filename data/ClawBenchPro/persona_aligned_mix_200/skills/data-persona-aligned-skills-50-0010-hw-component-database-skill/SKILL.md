---
name: "Hardware Component Database Skill (LLM)"
description: "企业内部的智能硬件组件手册与勘误库系统。该系统集成了所有在研硬件的 Datasheet、Errata（勘误表）以及相关固件问题的记录。当你需要确认某款芯片的行为逻辑、寄存器定义或报错原因时，可以向该系统发起查询。"
aliases:
  - hw_component_database_skill
  - data-persona-aligned-skills-50-0010-hw-component-database-skill
---

# Hardware Component Database Skill (LLM)

企业内部的智能硬件组件手册与勘误库系统。该系统集成了所有在研硬件的 Datasheet、Errata（勘误表）以及相关固件问题的记录。当你需要确认某款芯片的行为逻辑、寄存器定义或报错原因时，可以向该系统发起查询。

## Usage
执行 Python 脚本查询：
`python hw_component_database_skill.py "<your_query>"`

- `<your_query>`: 请包含芯片型号以及你需要询问的具体寄存器地址或现象（例如："查询 PMIC-3400 的 0x11 寄存器为何报错 NACK"）
