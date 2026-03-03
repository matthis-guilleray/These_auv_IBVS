#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
import cv2
import gi
import numpy as np
from sensor_msgs.msg import Image, PointCloud2 #new This line imports the ROS 2 message type 
from cv_bridge import CvBridge  #new converting between ROS Image messages and OpenCV images (numpy arrays).
import rclpy
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseArray, Pose, Point
from std_msgs.msg import Header
from . import class_base as bc

from .Tracking import ModuleTracking as mT
from .Tracking.common import utilsLogger as logMod
from .ROV import utilsRos as uRos

class PointsSelection(bc.BaseRos2):

    image = None
    tracker:mT.VisualTracking
    cv_bridge = CvBridge()

    def __init__(self, rclpy, name="BaseRos2", frequency=30):
        super().__init__(rclpy, name, frequency)
        self.log("info", "Init Points Selection object")
        self.__subscribers()
        self.__publishers()
        self.tracker = mT.VisualTracking(self)

    def update(self):
        image = self.image
        if (image is not None):
            self.log("info", "Selecting points on an image")
            self.tracker.is_selecting = True
            self.tracker.on_image(image)
            
            # self.__exit__()


    def _callback_on_frame(self, image):
        self.log("info", "Frame received")
        cv_image = self.cv_bridge.imgmsg_to_cv2(image)
        self.image = cv_image


    def __subscribers(self):
        self.subscriber_image = self.create_subscription(Image, "/camera/image", self._callback_on_frame, 10)

    def __publishers(self):
        self.publisher_pts_selected = self.create_publisher(PoseArray, '/camera/points/selected', 10) 

    def publish(self, topic, data, verbose):
        if "Tracking/pointsSelected" in topic:
            self.log("info", f"Publishing some points : {data}")
            msg = uRos.points_to_poseArray(data)
            self.publisher_pts_selected.publish(msg)




    
def main(argv=None):
    rclpy.init(args=argv)
    blueRov = PointsSelection(frequency=30, name="BlueRov", rclpy=rclpy)
    blueRov.node_run()

if __name__ == '__main__':
    main()

    