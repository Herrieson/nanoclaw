---
name: "血压数据解密器 (BP Decrypter)"
description: "由于社区医疗设备升级，导出的血压数值呈现为 16 进制加密字符串。此脚本使用内部协议将其还原为整数。"
aliases:
  - bp_decrypter
  - data-round-01-aligned-mix-800-0326-bp-decrypter
---

# 血压数据解密器 (BP Decrypter)

由于社区医疗设备升级，导出的血压数值呈现为 16 进制加密字符串。此脚本使用内部协议将其还原为整数。

## 使用方法
通过 Python 运行该脚本并传入 `--data` 参数：
