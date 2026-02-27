import rclpy
import traceback
import numpy as np
import math
from rclpy.node import Node
import rclpy.timer
from rclpy.qos import QoSProfile, QoSReliabilityPolicy, QoSHistoryPolicy
from struct import pack, unpack
from std_msgs.msg import Int16, Float64, Empty, Float64MultiArray, String
from sensor_msgs.msg import Joy, Imu, FluidPressure, LaserScan
from mavros_msgs.srv import CommandLong, SetMode, StreamRate
from mavros_msgs.msg import OverrideRCIn, Mavlink
from mavros_msgs.srv import EndpointAdd
from geometry_msgs.msg import Twist
from datetime import datetime
from rclpy.logging import get_logger



class BaseRos2(Node):
    dT:float
    name:str
    timer_update:rclpy.timer.Timer

    def __init__(self, name="BaseRos2", frequency=30):
        super().__init__(name)
        self.dT = 1/frequency
        self._log = self.get_logger()
        self.timer_update = self.create_timer(self.dT, self.update)
        pass

    def __enter__(self):
        self.enter()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.exit()
        self.timer_update.cancel()
        # ROS call : 
        self.destroy_node()

    def log(self, log_level, data, once = False, skip_first = False):
        now = datetime.now()
        f = now.strftime("%m-%d - %H:%M:%S.%f")
        text = f"{f} - {str(data)}"

        match log_level:
            case "debug":
                
                self.get_logger().info(text, once=once, skip_first=skip_first)
            case "info":
                self.get_logger().info(text, once=once, skip_first=skip_first)
            case "warning":
                self.get_logger().info(text, once=once, skip_first=skip_first)
            case "error":
                self.get_logger().info(text, once=once, skip_first=skip_first)
            case _: 
                raise ValueError(f"Log level not found {log_level}")

    def update(self):
        raise NotImplementedError("This function should have been implemented")

    def exit(self):
        raise NotImplementedError("This function should have been implemented")

    def enter(self):
        raise NotImplementedError("This function should have been implemented")

    def node_run(self):
        # rclpy.init(args=args)
        with self as e:
            rclpy.spin(e)



if __name__ == "__main__":
    BaseRos2.node_run()