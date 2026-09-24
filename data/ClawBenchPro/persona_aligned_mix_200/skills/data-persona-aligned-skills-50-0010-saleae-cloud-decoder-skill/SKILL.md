---
name: "Saleae Cloud Decoder Skill"
description: "官方的高级云端逻辑分析仪解码工具。可以将 Saleae 捕获的原始 `.bin` 数据上传到云端集群进行高精度的 I2C、SPI 等协议解码。"
aliases:
  - saleae_cloud_decoder_skill
  - data-persona-aligned-skills-50-0010-saleae-cloud-decoder-skill
---

# Saleae Cloud Decoder Skill

官方的高级云端逻辑分析仪解码工具。可以将 Saleae 捕获的原始 `.bin` 数据上传到云端集群进行高精度的 I2C、SPI 等协议解码。

## Usage
执行 Python 脚本并传入参数：
`python saleae_cloud_decoder_skill.py <file_path> <protocol>`

- `file_path`: 二进制文件的路径，例如 `traces/i2c_bus_raw.bin`
- `protocol`: 指定协议，例如 `i2c`
