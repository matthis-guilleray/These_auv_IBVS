import rclpy
import numpy as np
from mavros_msgs.srv import CommandLong, StreamRate
from mavros_msgs.msg import OverrideRCIn
from geometry_msgs.msg import Twist
import IBVS_ROV.Utils.utilsValue as uVal


def _map_val_node(node, value):
    return uVal.map_value_saturation(value, node.param_pwm_min, node.param_pwm_max)

def _generate_rcin_msg_neutral():
    msg_override = OverrideRCIn()
    msg_override.channels[0] = 1500
    msg_override.channels[1] = 1500
    msg_override.channels[2] = 1500
    msg_override.channels[3] = 1500
    msg_override.channels[4] = 1500
    msg_override.channels[5] = 1500
    for i in range(6, 17+1):
        if i == 6 or i == 7:
            msg_override.channels[i] = 1500
        else:
            msg_override.channels[i] = 0
        
    return msg_override



def _set_override_rcin_msg(node, msg:OverrideRCIn):
    node.publisher_override_rc_in.publish(msg)


def set_pwm_from_channel(node, channel_index, channel_value):
    msg = _generate_rcin_msg_neutral()
    channel_value = np.uint(channel_value)
    if channel_index <= 6:
        channel_value = np.uint(uVal.map_val_node(node, channel_value))
    elif channel_index <= 18 : 
        channel_value = uVal.map_value_saturation(channel_value, 0, node.param_pwm_max)
        
    msg.channels[channel_index] = channel_value
    _set_override_rcin_msg(node, msg)

def set_pwm_neutral(node):
    msg = _generate_rcin_msg_neutral()
    _set_override_rcin_msg(node, msg)

def set_pwm_speed(node, 
                  channel_pitch, 
                  channel_roll, 
                  channel_throttle, 
                  channel_yaw, 
                  channel_forward,
                  channel_lateral,
                  channel_other = []):
    msg = _generate_rcin_msg_neutral()
    msg.channels[0] = _map_val_node(node, channel_pitch)  # pulseCmd[4]--> pitch
    msg.channels[1] = _map_val_node(node, channel_roll)  # pulseCmd[3]--> roll
    msg.channels[2] = _map_val_node(node, channel_throttle)  # pulseCmd[2]--> heave
    msg.channels[3] = _map_val_node(node, channel_yaw)  # pulseCmd[5]--> yaw
    msg.channels[4] = _map_val_node(node, channel_forward)  # pulseCmd[0]--> surge
    msg.channels[5] = _map_val_node(node, channel_lateral)  # pulseCmd[1]--> sway
    for i in range(6, 17+1):
        msg.channels[i] = 0
        if (len(channel_other) > i-6):
            msg.channels[i] = channel_other[i-6]

    _set_override_rcin_msg(node, msg)

def _map_value(node, value, gain):
        return uVal.map_value_scale(value, gain=gain*node.param_gain_global, neutral=node.param_neutral, scale=node.param_neutral - node.param_pwm_min)

def set_speed(node, cmd:Twist):
    roll_left_right = _map_value(node, cmd.angular.x, node.param_gain_rx)
    yaw_left_right = _map_value(node, cmd.angular.z, node.param_gain_rz)
    ascend_descend = _map_value(node, cmd.linear.z, node.param_gain_vz)
    forward_reverse = _map_value(node, cmd.linear.x, node.param_gain_vx)
    lateral_left_right = _map_value(node, cmd.linear.y, node.param_gain_vy)
    pitch_left_right = _map_value(node, cmd.angular.y, node.param_gain_ry)


    set_pwm_speed(
        node, 
        pitch_left_right, 
        roll_left_right, 
        ascend_descend, 
        yaw_left_right, 
        forward_reverse,
        lateral_left_right
    )

def set_speed_neutral(node):
    set_pwm_neutral(node)




