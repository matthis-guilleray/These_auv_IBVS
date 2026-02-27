import rclpy
import traceback
import numpy as np
import math
from rclpy.node import Node
from rclpy.qos import QoSProfile, QoSReliabilityPolicy, QoSHistoryPolicy
from struct import pack, unpack
from std_msgs.msg import Int16, Float64, Empty, Float64MultiArray, String
from sensor_msgs.msg import Joy, Imu, FluidPressure, LaserScan
from mavros_msgs.srv import CommandLong, SetMode, StreamRate
from mavros_msgs.msg import OverrideRCIn, Mavlink
from mavros_msgs.srv import EndpointAdd
from geometry_msgs.msg import Twist
from . import baseClass as bc
from .ROV import communication as cmBR
from .ROV import utilsValue as uVal 

QOS_PROFILE = 10
BP_ARM = 7 # Start bp
BP_DISARM = 6 # Back bp
BP_MANUAL = 3 # Y bp
BP_AUTOM = 2 # X bp
BP_NEUTRAL = 0 # A button = 0
BP_MAX_INDEX = 7




class BlueRov(bc.BaseRos2):

    status_arm = False

    mode_requested = {
        "robot_arm":False,
        "robot_disarm":False,
        "control_manual":True,
        "control_autom":False,
        "control_neutral":False
    }
    



    def __init__(self, rclpy, frequency_main, name, ignore_arm = False):
        super(BlueRov, self).__init__(rclpy=rclpy, frequency=frequency_main, name=name)
        self.client_arming = cmBR.blueRov_create_client(self)
        if (ignore_arm == False):
            cmBR.set_disarm(self, self.client_arming)
            cmBR.set_stream_rate(self, 25)
        self._run_publishers()
        self._run_subscriber()


    def enter(self):
        """
        Super function called on node startup
        """
        self.log("info", "Enter BlueRov")
        return self
    
    def exit(self):
        """
        Super function called on node stop
        """
        self.log("info", "Ending RosPin")
        cmBR.set_disarm(self, self.client_arming)
        if self.status_arm == True:
            cmBR.set_disarm(self)

    def update(self):
        """
        Super function called on a timer of frequency_main
        """
        if self.mode_requested["robot_arm"] == True and self.status_arm == False:
            cmBR.set_arm(self, self.client_arming)
            self.mode_requested["robot_disarm"] = False
            self.mode_requested["robot_arm"] = False

        if self.mode_requested["robot_disarm"] == True:
            self.log("info", "Hello")
            cmBR.set_disarm(self, self.client_arming)
            self.mode_requested["robot_disarm"] = False
            self.mode_requested["robot_arm"] = False

        if self.mode_requested["control_neutral"] == True:
            cmBR.set_override_rcin_neutral(self)


    def joystick_is_mode_manual(self):
        return self.mode_requested["control_manual"]
    
    def joystick_is_automatic(self):
        return self.mode_requested["control_autom"]
    
    def _callback_joy(self, data):
        self.log("info", data.buttons)
        if data.buttons[BP_ARM] == 1 :
            self.log("info", "Arming")
            self.mode_requested["robot_arm"] = True
            self.mode_requested["robot_disarm"] = False
        if data.buttons[BP_DISARM] == 1:
            self.log("info", "Disarming")
            self.mode_requested["robot_disarm"] = True
            self.mode_requested["robot_arm"] = False

        if data.buttons[BP_MANUAL] == 1:
            self.log("info", "Manual")
            self.mode_requested["control_manual"] = True
            self.mode_requested["control_autom"] = False
        if data.buttons[BP_AUTOM] == 1:
            self.log("info", "Autom")
            self.mode_requested["control_manual"] = False
            self.mode_requested["control_autom"] = True
        
        self.mode_requested["control_neutral"] = data.buttons[BP_NEUTRAL]
        
    
    def _callback_vel(self, cmd_vel):
        # Extract cmd_vel message
        roll_left_right = uVal.map_value_scale(cmd_vel.angular.x)
        yaw_left_right = uVal.map_value_scale(cmd_vel.angular.z)
        ascend_descend = uVal.map_value_scale(cmd_vel.linear.z)
        forward_reverse = uVal.map_value_scale(-cmd_vel.linear.x)
        lateral_left_right = uVal.map_value_scale(cmd_vel.linear.y)
        pitch_left_right = uVal.map_value_scale(cmd_vel.angular.y)

        if bool(self.joystick_is_mode_manual()):
            cmBR.set_override_rcin(self, pitch_left_right, roll_left_right, ascend_descend, yaw_left_right, forward_reverse,
                             lateral_left_right)


    def _callback_imu(self, data):
        pass


    def _run_subscriber(self):
        qos_profile = QoSProfile(
            reliability=QoSReliabilityPolicy.BEST_EFFORT,
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=1
        )

        self.subscriber_joystick = self.create_subscription(Joy, "/bluerov2/joy", self._callback_joy, qos_profile=qos_profile)
        self.subscriber_cmdvel = self.create_subscription(Twist, "/bluerov2/cmd_vel", self._callback_vel, qos_profile=qos_profile)
        self.subscriber_imu = self.create_subscription(Imu, "/bluerov2/imu/data", self._callback_imu, qos_profile=qos_profile)


    def _run_publishers(self):
        self.publisher_override_rc_in = self.create_publisher(OverrideRCIn, "/bluerov2/rc/override", QOS_PROFILE)
        self.publisher_angle_degrees = self.create_publisher(Twist, '/bluerov2/angle_degree', QOS_PROFILE)
        self.publisher_depth = self.create_publisher(Float64, '/bluerov2/depth', QOS_PROFILE)
        self.publisher_angular_velocity = self.create_publisher(Twist, '/bluerov2/angular_velocity', QOS_PROFILE)
        self.publisher_linear_velocity = self.create_publisher(Twist, '/bluerov2/linear_velocity', QOS_PROFILE)


def main(argv=None):
    rclpy.init(args=argv)
    blueRov = BlueRov(frequency_main=30, name="BlueRov", rclpy=rclpy)
    blueRov.node_run()
    rclpy.shutdown()

if __name__ == '__main__':
    main()