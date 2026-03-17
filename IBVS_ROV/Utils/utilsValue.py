from geometry_msgs.msg import PoseArray, Pose, Point, Vector3, Twist


def map_value_scale(value, neutral = 1500, scale = 400, gain = 1):
        # Correction_Vel and joy between -1 et 1
        # scaling for publishing with setOverrideRCIN values between 1100 and 1900
        # neutral point is 1500
        value = value * gain
        pulse_width = value * scale + neutral

        return int(pulse_width)


def map_value_saturation(value, min, max):
        # Saturation
    if value > max:
        value = max
    if value < min:
        value = min
    return int(value)


def twist_cap(vel:Twist, value):
    vel.angular.x = vel.angular.x if vel.angular.x >= value else value
    vel.angular.y = vel.angular.y if vel.angular.y >= value else value
    vel.angular.z = vel.angular.z if vel.angular.z >= value else value

    vel.linear.x = vel.linear.x if vel.linear.x >= value else value
    vel.linear.y = vel.linear.y if vel.linear.y >= value else value
    vel.linear.z = vel.linear.z if vel.linear.z >= value else value

    return vel


def handle_z_value(list_points, zValue_isSet, zValue_default):
    out_list = []
    for point in list_points:

        if len(point) < 3:
            # Handling missing Z
            if zValue_default is not None:
                point.append(zValue_default)
            else:
                raise ValueError("Z missing and no zValue isSet ")
            
        if zValue_isSet == True and zValue_default is not None:
            point[2] = zValue_default

        out_list.append([point[0], point[1], point[2]])
    return out_list