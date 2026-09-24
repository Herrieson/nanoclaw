---
name: "art_currency_converter_skill"
description: "Converts ArtCoin (AC) to USD based on the event date's valuation."
aliases:
  - art_currency_converter_skill
  - data-round-01-aligned-mix-800-0394-art-currency-converter-skill
---

# art_currency_converter_skill

Converts ArtCoin (AC) to USD based on the event date's valuation.

**Parameters:**
- `amount`: The amount in ArtCoin (AC).
- `date`: The date of the transaction (YYYY-MM-DD).

**Returns:**
- A JSON object with the `usd_equivalent` and the `exchange_rate` used.
