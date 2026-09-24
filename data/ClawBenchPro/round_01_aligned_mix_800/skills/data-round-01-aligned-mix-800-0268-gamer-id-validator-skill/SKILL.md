---
name: "gamer_id_validator_skill"
description: "Queries the official League Database to retrieve player age based on their `Gamer_Auth_ID`."
aliases:
  - gamer_id_validator_skill
  - data-round-01-aligned-mix-800-0268-gamer-id-validator-skill
---

# gamer_id_validator_skill

## Description
Queries the official League Database to retrieve player age based on their `Gamer_Auth_ID`.

## Usage
`python skills/data_round_01_aligned_mix_800_0268/gamer_id_validator_skill.py --id <Gamer_Auth_ID>`

## Parameters
- `--id`: The unique player ID (e.g., ID_001).

## Returns
A JSON object with `id`, `username`, and `age`.
