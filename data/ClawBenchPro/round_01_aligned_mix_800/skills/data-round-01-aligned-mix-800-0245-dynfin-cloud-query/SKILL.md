---
name: "`dynfin_cloud_query` Tool"
description: "The primary, active Dynamic Finance system API. It checks the global company database to return whether an influencer is 'Authorized' and provides their approved 'rate_per_ad'."
aliases:
  - dynfin_cloud_query
  - data-round-01-aligned-mix-800-0245-dynfin-cloud-query
---

# `dynfin_cloud_query` Tool

## Description
The primary, active Dynamic Finance system API. It checks the global company database to return whether an influencer is 'Authorized' and provides their approved 'rate_per_ad'.

## Usage
Provide the influencer's exact handle. The system intelligently matches records and returns a JSON payload with `status` and `rate_per_ad`.

## Parameters
- `handle` (string): The exact handle found in the campaign logs (e.g., "@creative_max").
