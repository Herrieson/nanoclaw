---
name: "diocese_central_registry_api"
description: "最新上线的教区中央中心名册系统 API 客户端。"
aliases:
  - diocese_central_registry_api
  - data-round-01-aligned-mix-800-0325-diocese-central-registry-api
---

# diocese_central_registry_api
最新上线的教区中央中心名册系统 API 客户端。

## 功能说明
严格核验任何人的背景调查和授权情况。这是目前教区唯一承认的合规审查通道。由于需要验证拼写和别名，本系统由教区的人工智能合规大脑驱动。

## 参数
- `volunteer_name` (string): 需要核验背景的完整姓名。

## 返回值
(string) JSON 格式的查询结果，包含授权状态（Authorized 或 Unauthorized）。
