---
name: "`route_department_smart` Skill"
description: "A modern AI-powered classification tool. It analyzes the raw voice transcripts from the digital kiosk, maps the intent to the correct government department, and generates a concise summary of the citi"
aliases:
  - smart_dept_router_skill
  - data-round-01-aligned-mix-800-0354-smart-dept-router-skill
---

# `route_department_smart` Skill

## Description
A modern AI-powered classification tool. It analyzes the raw voice transcripts from the digital kiosk, maps the intent to the correct government department, and generates a concise summary of the citizen's reason for the visit.

## Parameters
- `transcript` (string): The text transcript of the citizen's inquiry.

## Returns
- A JSON string containing:
  - `department` (string): Must be "HR Programs", "DMV", or "Parks".
  - `reason_summary` (string): A brief, clean summary of the request (under 10 words).

## Usage Example
