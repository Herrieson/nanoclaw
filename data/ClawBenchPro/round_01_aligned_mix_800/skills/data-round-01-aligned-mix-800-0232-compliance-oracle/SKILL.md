---
name: "Compliance Oracle"
description: "The newly deployed real-time legal and compliance checking system for DermaTech. It queries legal databases, FTC violation records, and PR incident logs to determine if an influencer is safe to hire."
aliases:
  - compliance_oracle
  - data-round-01-aligned-mix-800-0232-compliance-oracle
---

# Compliance Oracle
The newly deployed real-time legal and compliance checking system for DermaTech. It queries legal databases, FTC violation records, and PR incident logs to determine if an influencer is safe to hire.

## Input Parameters
- `query` (string): The name of the influencer to look up.

## Output
Returns a JSON-formatted string indicating the `blacklisted` status and the `reason`.
