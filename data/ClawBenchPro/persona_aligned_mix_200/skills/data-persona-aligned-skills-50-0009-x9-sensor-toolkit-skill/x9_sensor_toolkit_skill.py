def adc_to_celsius(adc_value: int) -> float:
    """
    Converts X-9 Thermal ADC raw integer to Celsius using a calibrated engineering curve.
    """
    try:
        adc_val = int(adc_value)
    except (ValueError, TypeError):
        return -999.0
        
    if adc_val < 0 or adc_val > 65535:
        return -999.0
        
    # Proprietary linear/non-linear thermal compensation curve for X-9
    temp_celsius = (adc_val * 0.05) - 40.0
    return round(temp_celsius, 2)
