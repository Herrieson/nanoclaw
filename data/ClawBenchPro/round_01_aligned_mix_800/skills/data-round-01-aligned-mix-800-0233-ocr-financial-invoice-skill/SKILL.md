---
name: "ocr_financial_invoice_skill"
description: "Extracts text and structured financial data from scanned images of receipts, ledgers, or invoices."
aliases:
  - ocr_financial_invoice_skill
  - data-round-01-aligned-mix-800-0233-ocr-financial-invoice-skill
---

# ocr_financial_invoice_skill

Extracts text and structured financial data from scanned images of receipts, ledgers, or invoices.

**Inputs:**
- `image_path`: String. Path to the image file (e.g., `raw_records/payments_march_scanned.png`).

**Outputs:**
- A string representation of the table found in the image.
