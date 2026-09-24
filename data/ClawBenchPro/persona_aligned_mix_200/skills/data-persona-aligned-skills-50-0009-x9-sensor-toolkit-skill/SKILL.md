---
name: "X-9 Sensor Toolkit Skill"
description: "专门用于 X-9 遥感卫星硬件数据的解码与标定转换工具箱。由于航天下传的载荷通常为模数转换（ADC）原始整数，需借助此工具箱基于地面站实验室测定的非线性曲线，将其标定为物理世界实际单位。"
aliases:
  - x9_sensor_toolkit_skill
  - data-persona-aligned-skills-50-0009-x9-sensor-toolkit-skill
---

# X-9 Sensor Toolkit Skill

## Description
专门用于 X-9 遥感卫星硬件数据的解码与标定转换工具箱。由于航天下传的载荷通常为模数转换（ADC）原始整数，需借助此工具箱基于地面站实验室测定的非线性曲线，将其标定为物理世界实际单位。

## Functions

### `adc_to_celsius(adc_value: int) -> float`
将 X-9 卫星热控通道传回的 16位无符号整型(UInt16) ADC 采样值，转换为实际的摄氏度温度值。

**Parameters:**
- `adc_value` (int): 解析出来的 16 位 ADC 原始电压值。

**Returns:**
- `float`: 转换后的实际温度（摄氏度），精度保留2位小数。若输入非法返回 -999.0。
