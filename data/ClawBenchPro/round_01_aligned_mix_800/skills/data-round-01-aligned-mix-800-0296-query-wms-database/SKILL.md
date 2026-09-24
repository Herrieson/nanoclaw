---
name: "query_wms_database.py"
description: "This is the next-generation Warehouse Management System (WMS) API CLI tool. It connects directly to the cloud inventory database."
aliases:
  - query_wms_database
  - data-round-01-aligned-mix-800-0296-query-wms-database
---

# query_wms_database.py

This is the next-generation Warehouse Management System (WMS) API CLI tool. It connects directly to the cloud inventory database. 

Since the new smart scanners do not export comprehensive logs (such as product names, minimum stock requirements, or human-readable status codes), you can use this tool to query that missing information.

## Usage
Run the script using Python and pass your query via the `--query` argument. You can ask for information about specific SKUs, or ask to decode specific condition codes.
