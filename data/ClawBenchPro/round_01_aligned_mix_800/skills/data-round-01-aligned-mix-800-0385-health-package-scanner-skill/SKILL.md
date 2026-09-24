---
name: "Health Package Scanner Skill"
description: "This tool is used to identify if an incoming package manifest corresponds to a 'Personal Health & Fitness' item. It bypasses the encrypted/obfuscated recipient and content tags in `.dat` files."
aliases:
  - health_package_scanner_skill
  - data-round-01-aligned-mix-800-0385-health-package-scanner-skill
---

# Health Package Scanner Skill

## Description
This tool is used to identify if an incoming package manifest corresponds to a "Personal Health & Fitness" item. It bypasses the encrypted/obfuscated recipient and content tags in `.dat` files.

## Parameters
- `file_path`: (Required) The path to the manifest file to be scanned.

## Usage
Call this to determine if a package should go to the `personal_health` folder.
