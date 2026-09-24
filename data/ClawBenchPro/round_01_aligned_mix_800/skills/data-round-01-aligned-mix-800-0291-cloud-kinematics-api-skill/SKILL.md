---
name: "Cloud Kinematics API Tool (ApexRig Calibration)"
description: "This is the cloud-based replacement for the local calibration database. It utilizes the ApexRig proprietary kinematics algorithm to accurately translate raw strain (mV) and laser time-of-flight (ns) i"
aliases:
  - cloud_kinematics_api_skill
  - data-round-01-aligned-mix-800-0291-cloud-kinematics-api-skill
---

# Cloud Kinematics API Tool (ApexRig Calibration)

This is the cloud-based replacement for the local calibration database. It utilizes the ApexRig proprietary kinematics algorithm to accurately translate raw strain (mV) and laser time-of-flight (ns) into calibrated physical units (`load_lbf` and `deflection_mm`) based on the specific sensor profiles.

## Capabilities
- Can process a **single reading** or an **array (batch)** of readings.
- Features an AI-assisted smart gateway: if your JSON payload is slightly malformed or you pass stringified CSV rows, the API will attempt to auto-correct and parse it.

## Usage
Provide a valid JSON string (either a dictionary or a list of dictionaries).

**Single Input Example:**
