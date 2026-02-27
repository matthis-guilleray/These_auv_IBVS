

def map_value_scale(value, neutral = 1500, scale = 400):
        # Correction_Vel and joy between -1 et 1
        # scaling for publishing with setOverrideRCIN values between 1100 and 1900
        # neutral point is 1500
        pulse_width = value * scale + neutral

        return int(pulse_width)


def map_value_saturation(value, min, max):
    # Saturation
    if value > max:
        value = max
    if value < min:
        value = min
    return value