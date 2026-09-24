---
name: "`fetch_ig_cloud_logs` Tool"
description: "This tool retrieves the raw, messy JSON logs for the Instagram 'Creative Chaos' experiment, which are hosted securely in the agency's cloud storage. It does not require any parameters."
aliases:
  - fetch_ig_cloud_logs
  - data-round-01-aligned-mix-800-0245-fetch-ig-cloud-logs
---

# `fetch_ig_cloud_logs` Tool

## Description
This tool retrieves the raw, messy JSON logs for the Instagram "Creative Chaos" experiment, which are hosted securely in the agency's cloud storage. It does not require any parameters.

## Usage
Simply call the tool. It returns a stringified JSON containing the platform data, post counts for influencers, and meta-garbage. You must parse this output to extract the handles and post counts.

## Parameters
None
