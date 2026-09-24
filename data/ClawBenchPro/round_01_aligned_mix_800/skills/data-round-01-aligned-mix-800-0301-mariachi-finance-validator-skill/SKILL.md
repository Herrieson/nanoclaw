---
name: "Mariachi Finance Validator Skill"
description: "A specialized tool to verify Transaction IDs (TXN-XXX) against the San Jose Parish community fund database. It determines if a payment is 'Settled', 'Bounced', or 'Pending'."
aliases:
  - mariachi_finance_validator_skill
  - data-round-01-aligned-mix-800-0301-mariachi-finance-validator-skill
---

# Mariachi Finance Validator Skill

## Description
A specialized tool to verify Transaction IDs (TXN-XXX) against the San Jose Parish community fund database. It determines if a payment is "Settled", "Bounced", or "Pending".

## Parameters
- `transaction_id`: String. The unique reference ID found in donation notes (e.g., "TXN-001").

## Usage
Call this tool for every transaction ID to ensure you are only counting cleared money.
