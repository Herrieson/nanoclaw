---
name: "spacecraft_quaternion_normalizer"
description: "A flight-certified mathematical utility used to strictly normalize a 4-dimensional quaternion vector. It ensures that the magnitude of the quaternion `sqrt(w^2 + x^2 + y^2 + z^2)` is exactly 1.0. This"
aliases:
  - spacecraft_quaternion_normalizer
  - data-persona-aligned-skills-50-0033-spacecraft-quaternion-normalizer
---

# spacecraft_quaternion_normalizer

## Description
A flight-certified mathematical utility used to strictly normalize a 4-dimensional quaternion vector. It ensures that the magnitude of the quaternion `sqrt(w^2 + x^2 + y^2 + z^2)` is exactly 1.0. This tool MUST be used to clean up any raw telemetry quaternion data before it can be safely ingested by the Flight Dynamics Simulator, otherwise, math singularities will cause the simulation to crash.

## Parameters
- `q_w` (float, required): The scalar component.
- `q_x` (float, required): The first vector component.
- `q_y` (float, required): The second vector component.
- `q_z` (float, required): The third vector component.

## Returns
- `dict`: A dictionary containing the normalized quaternion components `{"q_w": float, "q_x": float, "q_y": float, "q_z": float}`.
