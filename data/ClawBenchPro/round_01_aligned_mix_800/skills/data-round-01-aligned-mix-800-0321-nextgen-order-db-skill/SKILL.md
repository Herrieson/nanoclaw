---
name: "NextGen Order Database Query"
description: "Use this tool to securely query detailed product information (product name, quantity, unit price) for a specific order ID using the company's new cloud-based ERP API."
aliases:
  - nextgen_order_db_skill
  - data-round-01-aligned-mix-800-0321-nextgen-order-db-skill
---

# NextGen Order Database Query
Use this tool to securely query detailed product information (product name, quantity, unit price) for a specific order ID using the company's new cloud-based ERP API.

## Input Parameters
- `order_id` (string): The unique identifier of the order (e.g., "1001").

## Output
Returns a JSON string containing the `order_id`, `product_name`, `quantity`, and `unit_price`.
Please note that data migrated from the old system might still contain raw or unformatted strings (e.g., currency symbols, trailing spaces).

## Example
