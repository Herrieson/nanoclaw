---
name: "xarray_dask_cluster_skill"
description: "基于 Dask 分布式计算框架的新一代气象数据多维数组（Xarray）分析 API。该接口直接与超算中心的底层存储卷挂载，无需指定单个本地文件路径，可通过自然语言和参数直接对全体 GCM 输出快照进行高阶查询。"
aliases:
  - xarray_dask_cluster_skill
  - data-persona-aligned-skills-50-0027-xarray-dask-cluster-skill
---

# xarray_dask_cluster_skill

## Description
基于 Dask 分布式计算框架的新一代气象数据多维数组（Xarray）分析 API。该接口直接与超算中心的底层存储卷挂载，无需指定单个本地文件路径，可通过自然语言和参数直接对全体 GCM 输出快照进行高阶查询。

## Parameters
- `query` (str): 用自然语言描述你希望查询的数据需求。必须包含目标 `Rank ID` 和关注的 `变量名(如 T, U, V, Q)`。

## Usage
