---
name: "Art Registry Lookup (ArtRegistry-Pro)"
description: "Official interface for the Global Art Sponsorship Registry. Validates whether an artist is approved for corporate-funded acquisitions."
aliases:
  - art_authenticator_lookup_skill
  - data-round-01-aligned-mix-800-0313-art-authenticator-lookup-skill
---

# Art Registry Lookup (ArtRegistry-Pro)

## Description
Official interface for the Global Art Sponsorship Registry. Validates whether an artist is approved for corporate-funded acquisitions.

## Parameters
- `artist_name`: (required) String. The name of the artist to check.

## Response
Returns a status: "ACTIVE" (Authorized), "INACTIVE" (Unauthorized), or "NOT_FOUND".
