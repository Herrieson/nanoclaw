---
name: "Legacy Order Database Query"
description: "Use this tool to query product information (product name, quantity, unit price) for a specific order ID using the company's legacy ERP system."
aliases:
  - legacy_order_db_skill
  - data-round-01-aligned-mix-800-0321-legacy-order-db-skill
---

# Legacy Order Database Query
Use this tool to query product information (product name, quantity, unit price) for a specific order ID using the company's legacy ERP system. 
This was the primary system before the recent v2.0 migration.

## Input Parameters
- `order_id` (string): The unique identifier of the order (e.g., "1001").

## Output
Returns a JSON string containing the order details, or an error message if the system is unreachable.

## Example
