---
name: "cultural_artifact_authenticator_skill"
description: "Verifies if a specific artifact is registered in the Global Cultural Heritage Database."
aliases:
  - cultural_artifact_authenticator_skill
  - data-round-01-aligned-mix-800-0224-cultural-artifact-authenticator-skill
---

# cultural_artifact_authenticator_skill

Verifies if a specific artifact is registered in the Global Cultural Heritage Database.

**Parameters:**
- `artifact_name`: The name of the item to verify.
- `holder_name`: The name of the person presenting it.

**Returns:**
- JSON string with `status`: "Authenticated" or "Unauthenticated".
