---
name: "Sigrok CLI Decoder Skill"
description: "开源的本地逻辑分析仪解码工具套件 (sigrok-cli)。支持轻量级、本地化的总线解码，能将二进制捕获数据还原为可读的通信日志。"
aliases:
  - sigrok_cli_decoder_skill
  - data-persona-aligned-skills-50-0010-sigrok-cli-decoder-skill
---

# Sigrok CLI Decoder Skill

开源的本地逻辑分析仪解码工具套件 (sigrok-cli)。支持轻量级、本地化的总线解码，能将二进制捕获数据还原为可读的通信日志。

## Usage
执行 Python 脚本并传入参数：
`python sigrok_cli_decoder_skill.py --file <file_path> --protocol <protocol>`

- `--file`: 二进制文件的路径。
- `--protocol`: 总线协议名称，仅支持 `i2c`, `spi`, `uart` 等。
