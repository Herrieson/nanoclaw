---
name: "`bicsi_cloud_api`"
description: "The new modern Cloud-based API for querying the national BICSI certification database. It resolves technician names dynamically and returns their valid, active telecom certifications (e.g., FiberOptic"
aliases:
  - bicsi_cloud_api
  - data-round-01-aligned-mix-800-0222-bicsi-cloud-api
---

# `bicsi_cloud_api`

## Description
The new modern Cloud-based API for querying the national BICSI certification database. It resolves technician names dynamically and returns their valid, active telecom certifications (e.g., FiberOptic, Cat6, Safety, Basic).

## Parameters
- `query_name` (str): The name of the volunteer/technician to query.

## Returns
- (str): JSON string containing a list of active certifications.
