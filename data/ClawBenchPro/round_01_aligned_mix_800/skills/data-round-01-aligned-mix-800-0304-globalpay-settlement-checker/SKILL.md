---
name: "GlobalPay Settlement Checker"
description: "A command-line tool to verify the true bank settlement status of POS transactions. Due to chargebacks and delayed processing, a transaction marked as 'COMPLETED' in the local POS log may not have actu"
aliases:
  - globalpay_settlement_checker
  - data-round-01-aligned-mix-800-0304-globalpay-settlement-checker
---

# GlobalPay Settlement Checker

A command-line tool to verify the true bank settlement status of POS transactions. Due to chargebacks and delayed processing, a transaction marked as "COMPLETED" in the local POS log may not have actually cleared the bank.

## Usage
Provide the transaction ID (`tx_id`) as the only positional argument.
