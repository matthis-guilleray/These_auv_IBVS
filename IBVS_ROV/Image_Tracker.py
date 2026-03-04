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
from .Tracking.common import utilsImage as uImage
from .ROV import utilsRos as uRos


class ImageTracker(bc.BaseRos2):

    selected_points:PoseArray = None
    frame = None
    cv_bridge = CvBridge()
    vt:mT.VisualTracking
    fuse_distance = 30
    roi_factor = 2
    img_threshold = 254

    def __init__(self, rclpy=rclpy, name="Image Tracking class", frequency=30):
        super().__init__(rclpy=rclpy, name=name, frequency=frequency)
        self.vt = mT.VisualTracking(self)

        def nothing(x):
            pass

        if (self.get_parameter("open_window").value):
            cv2.namedWindow('image')
            if (self.get_parameter("trackbar").value):
                cv2.createTrackbar('Fuse disance','image',0,255,nothing)
                cv2.createTrackbar('ROI Factor','image',0,255,nothing)
                cv2.createTrackbar('IMG Threshold','image',0,255,nothing)
        
        


    def __parameters(self):
        self.declare_parameter("open_window", True)
        self.declare_parameter("trackbar", False)
        self.declare_parameter("debug", True)


    def update(self):
        if self.frame is not None:
            self.vt._image_base(self.frame.copy(), self.fuse_distance, self.roi_factor, self.img_threshold)
            if self.get_parameter("open_window").value :
                uImage.show_image(self.frame, name="image", timeout=1000)
                if self.get_parameter("trackbar").value:
                    self.roi_factor = cv2.getTrackbarPos('ROI Factor','image')
                    self.fuse_distance = cv2.getTrackbarPos('Fuse disance','image')
                    self.img_threshold = cv2.getTrackbarPos('IMG Threshold','image')


            self.frame = None
        


    def __publishers(self):
        self.publisher_pts_tracked = self.create_publisher(PoseArray, '/camera/points/detected/meter', 10) 
        self.publisher_pts_tracked_center = self.create_publisher(PoseArray, '/camera/points/detected/center', 10) 
        self.publisher_pts_tracked_raw = self.create_publisher(PoseArray, '/camera/points/detected/raw', 10) 

        self.publisher_mask = self.create_publisher(Image, "/camera/mask", 10)
        self.publisher_mask_colored = self.create_publisher(Image, "/camera/mask/colored", 10)


    def __subscribers(self):
        self.subscriber_image = self.create_subscription(Image, "/camera/image", self.__callback_on_frame, 10)
        self.subscriber_selected_points = self.create_subscription(PoseArray, "/camera/points/selected", self.__callback_on_selected_points, 10)

    def __callback_on_frame(self, data):
        self.log("info", "Frame received")
        cv_image = self.cv_bridge.imgmsg_to_cv2(data)
        self.frame = cv_image        

    def __callback_on_selected_points(self, data):
        pts = uRos.poseArray_to_points(data)
        self.selected_points = pts
        self.vt.pts_old_selected = self.selected_points

    def publish(self, topic, data, verbose):
        self.log(verbose, f"topic : {topic}, data : {data}")
        msg = None
        if "points" in topic:
            msg = uRos.points_to_poseArray(data)
        if 'mask' in topic:
             msg = self.cv_bridge.cv2_to_imgmsg(data, "rgb8")
        

        
        if topic == "Tracking/points/meter":
            self.log("info", f"Publsihing : {msg}")
            self.publisher_pts_tracked.publish(msg)
        elif topic == "Tracking/points/ibvs_frame":
            self.log("info", f"Publsihing : {msg}")
            self.publisher_pts_tracked_center.publish(msg)
        elif topic == "Tracking/points/camera_frame":
            self.log("info", f"Publsihing : {msg}")
            self.publisher_pts_tracked_raw.publish(msg)

        elif topic == "Tracking/mask/colored":
            self.log('info', "on mask")
            self.publisher_mask_colored.publish(msg)
            if self.get_parameter("open_window").value:
                uImage.show_image(data, name="mask colored")
        elif topic == "Tracking/mask":
            self.log('info', "on mask")
            self.publisher_mask.publish(msg)
            if self.get_parameter("open_window").value:
                uImage.show_image(data, name="mask")

def main(argv=None):
    rclpy.init(args=argv)
    blueRov = ImageTracker(frequency=30, name="Tracker", rclpy=rclpy)
    blueRov.node_run()

if __name__ == '__main__':
    main()
