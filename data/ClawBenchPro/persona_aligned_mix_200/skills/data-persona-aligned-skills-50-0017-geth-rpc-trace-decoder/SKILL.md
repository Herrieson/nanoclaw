---
name: "Geth RPC Trace Decoder"
description: "A proprietary tool designed to decode binary Geth EVM snapshot files (`.trace.dat`) exported by the underlying nodes. It strips the custom magic headers and decodes the payload into a standard JSON st"
aliases:
  - geth_rpc_trace_decoder
  - data-persona-aligned-skills-50-0017-geth-rpc-trace-decoder
---

# Geth RPC Trace Decoder

## Description
A proprietary tool designed to decode binary Geth EVM snapshot files (`.trace.dat`) exported by the underlying nodes. It strips the custom magic headers and decodes the payload into a standard JSON string.

## Usage
Provide the absolute or relative path to the `.trace.dat` file. The tool will return the decoded JSON string representing the EVM trace structure.

## Parameters
- `file_path` (string): The path to the EVMSNAP binary trace file.

## Returns
- A string containing the parsed JSON data, or an error message if the file is invalid or cannot be found.
