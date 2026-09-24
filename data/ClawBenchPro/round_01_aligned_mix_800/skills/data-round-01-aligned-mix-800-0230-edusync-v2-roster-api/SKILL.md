---
name: "edusync_v2_roster_api"
description: "The V2 version of the EduSync student database query system. Use this active API to verify if a student is officially enrolled in Mrs. Perić's classes."
aliases:
  - edusync_v2_roster_api
  - data-round-01-aligned-mix-800-0230-edusync-v2-roster-api
---

# edusync_v2_roster_api

## Description
The V2 version of the EduSync student database query system. Use this active API to verify if a student is officially enrolled in Mrs. Perić's classes. 

## Parameters
- `student_names` (string, required): The name of the student (or a comma-separated list of names) to verify against the official school roster.

## Output
Returns a JSON response indicating whether each queried student is officially enrolled in the class.
