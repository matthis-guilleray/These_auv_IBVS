import rclpy
import numpy as np
from mavros_msgs.srv import CommandLong, StreamRate
from mavros_msgs.msg import OverrideRCIn
from . import utilsValue as uVal

rc_in_override_pwm_max = 1900
rc_in_override_pwm_min = 1100


def blueRov_create_client(node, message_type = CommandLong, topic='/cmd/command'):
    node.log("info", f"Creating client : {topic}")
    node.log("info", f"Message : {message_type}")
    cli = node.create_client(message_type, topic)
    result = False
    while not result:
        result = cli.wait_for_service(timeout_sec=4.0)
        node.log("info", "Client requested", once=True)
        node.log("warning", "Timeout on client request", skip_first=True)
    return cli



def _message_create_arm(node):
    node.log("info", "creating arming msg the bluerov")
    req = CommandLong.Request()
    req.broadcast = False
    req.command = 400
    req.confirmation = 0
    req.param1 = 1.0
    req.param2 = 0.0
    req.param3 = 0.0
    req.param4 = 0.0
    req.param5 = 0.0
    req.param6 = 0.0
    req.param7 = 0.0
    return req

def _message_create_disarm(node):
    node.log("info", "creating disarming msg the bluerov")
    req = CommandLong.Request()
    req.broadcast = False
    req.command = 400
    req.confirmation = 0
    req.param1 = 0.0
    req.param2 = 0.0
    req.param3 = 0.0
    req.param4 = 0.0
    req.param5 = 0.0
    req.param6 = 0.0
    req.param7 = 0.0
    return req


def set_arm(node, client):
    node.log("info", "Arming the bluerov")
    req = _message_create_arm(node)
    _call_service(node, client=client, message=req, wait_for=False)
    node.status_arm_logic = None

def set_disarm(node, client):
    node.log("info", "Disarming the bluerov")
    req = _message_create_disarm(node)
    _call_service(node, client, req, wait_for=False)
    node.status_arm_logic = None


def set_stream_rate(node, rate):
    node.log('info', f"Setting stream rate : {rate}")
    client = blueRov_create_client(node, topic="/set_stream_rate", message_type=StreamRate)

    req = StreamRate.Request()
    req.stream_id = 0
    req.message_rate = rate
    req.on_off = True

    _call_service(node, client, req)

    node.log('info', "Done setting stream rate")



def _call_service(node, client, message, wait_for=False):
    node.log("info", client)
    future = client.call_async(message)
    rclpy.spin_until_future_complete(node, future, timeout_sec=3)

    if future.result() is not None:
        response = future.result()
        node.log("info", f"Response : {response}"
                
        )
    else:
        node.log("error",'Service call failed')



def set_override_rcin_neutral(node):
    channel_other = [1500, 1500]
    for i in range(8, 17):
        channel_other.append(0)
    set_override_rcin(node, 
        1500, 1500, 1500, 1500, 1500, 1500, channel_other=channel_other
    )


def set_override_rcin(node, 
                    channel_pitch, 
                    channel_roll, 
                    channel_throttle, 
                    channel_yaw, 
                    channel_forward,
                    channel_lateral,
                    channel_other = [],
                    ):
    
    node.log("info", f"p : {channel_pitch}, r : {channel_roll}, t : {channel_throttle}, y : {channel_yaw}, l : {channel_lateral}")
    node.log("info", f"Channel other :{str(channel_other)}")

    msg_override = OverrideRCIn()
    msg_override.channels[0] = np.uint(uVal.map_value_saturation(channel_pitch, rc_in_override_pwm_min, rc_in_override_pwm_max))  # pulseCmd[4]--> pitch
    msg_override.channels[1] = np.uint(uVal.map_value_saturation(channel_roll, rc_in_override_pwm_min, rc_in_override_pwm_max))  # pulseCmd[3]--> roll
    msg_override.channels[2] = np.uint(uVal.map_value_saturation(channel_throttle, rc_in_override_pwm_min, rc_in_override_pwm_max))  # pulseCmd[2]--> heave
    msg_override.channels[3] = np.uint(uVal.map_value_saturation(channel_yaw, rc_in_override_pwm_min, rc_in_override_pwm_max))  # pulseCmd[5]--> yaw
    msg_override.channels[4] = np.uint(uVal.map_value_saturation(channel_forward, rc_in_override_pwm_min, rc_in_override_pwm_max))  # pulseCmd[0]--> surge
    msg_override.channels[5] = np.uint(uVal.map_value_saturation(channel_lateral, rc_in_override_pwm_min, rc_in_override_pwm_max))  # pulseCmd[1]--> sway
    for i in range(6, 17+1):
        msg_override.channels[i] = 0
        if (len(channel_other) > i-6):
            msg_override.channels[i] = channel_other[i-6]
        
    node.publisher_override_rc_in.publish(msg_override)


def set_override_rcin_value(node, index, value):
    if index == 11 or index == 12 or index == 13:
        node.log("error", "DO NOT USE THOSE CHANNEL OR YOU WILL TURN CRAZY")
        node.log("info", "Value has been set to 0")
        # value = 0
    if index > 17:
        node.log("error", f"Index was too big : {index}")
        return 
    msg_override = OverrideRCIn()
    for i in range(0, 6):
        msg_override.channels[i] = 1500
    for i in range(6, 17+1)    :
        msg_override.channels[i] = 0

    if (index <= 5):
        msg_override.channels[index] = np.uint(uVal.map_value_saturation(value, rc_in_override_pwm_min, rc_in_override_pwm_max))
    else :
        msg_override.channels[index] = value if value <= 1900 else 1900

    node.log("info", f"Channel other :{str(msg_override.channels)}")
    node.publisher_override_rc_in.publish(msg_override)
            
    