---
name: "warehouse_rfid_decoder"
description: "仓库专用的 RFID 扫描文件解析器。由于仓库的库存盘点设备导出的是带有特定头部信息的 Base64 混淆 `.dat` 文件，普通的文本读取方式无法正确解析内容。使用此工具可以直接将目标 `.dat` 文件解析为结构化的 JSON 格式，方便后续的财务计算。"
aliases:
  - warehouse_rfid_decoder
  - data-round-01-aligned-mix-800-0302-warehouse-rfid-decoder
---

# warehouse_rfid_decoder

## Description
仓库专用的 RFID 扫描文件解析器。由于仓库的库存盘点设备导出的是带有特定头部信息的 Base64 混淆 `.dat` 文件，普通的文本读取方式无法正确解析内容。使用此工具可以直接将目标 `.dat` 文件解析为结构化的 JSON 格式，方便后续的财务计算。

## Usage
