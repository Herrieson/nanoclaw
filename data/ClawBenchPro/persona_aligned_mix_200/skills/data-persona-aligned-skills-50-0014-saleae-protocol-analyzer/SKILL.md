---
name: "Saleae Protocol Analyzer"
description: "A command-line tool to decode proprietary `.salb` (Saleae Binary) logic analyzer dump files into human-readable text formats mapping I2C, SPI, and UART transactions."
aliases:
  - saleae_protocol_analyzer
  - data-persona-aligned-skills-50-0014-saleae-protocol-analyzer
---

# Saleae Protocol Analyzer

A command-line tool to decode proprietary `.salb` (Saleae Binary) logic analyzer dump files into human-readable text formats mapping I2C, SPI, and UART transactions.

## Usage
Provide the file path to the `.salb` file.

## Example
`python saleae_protocol_analyzer.py dumps/logic_analyzer_ch0.salb`

## Outputs
The tool will print the decoded transaction sequence to standard output.
