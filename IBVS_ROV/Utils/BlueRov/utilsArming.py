import rclpy
import numpy as np
from mavros_msgs.srv import CommandLong, StreamRate
from mavros_msgs.msg import OverrideRCIn
import IBVS_ROV.Utils.ROS.utilsClient as uClient




def _message_create_arm():
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

def _message_create_disarm():
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
    req = _message_create_arm()
    uClient.call_service(node, client=client, message=req)
    node.status_arm_logic = None

def set_disarm(node, client):
    node.log("info", "Disarming the bluerov")
    req = _message_create_disarm()
    uClient.call_service(node, client, req, wait_for=False)
    node.status_arm_logic = None


def set_stream_rate(node, rate):
    node.log('info', f"Setting stream rate : {rate}")
    client = uClient.create_client(node, topic="/set_stream_rate", message_type=StreamRate)

    req = StreamRate.Request()
    req.stream_id = 0
    req.message_rate = rate
    req.on_off = True

    uClient.call_service(node, client, req)

    node.log('info', "Done setting stream rate")


