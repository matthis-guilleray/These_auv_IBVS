#!/usr/bin/env python3
import cv2
from sensor_msgs.msg import Image #new This line imports the ROS 2 message type 
from cv_bridge import CvBridge  #new converting between ROS Image messages and OpenCV images (numpy arrays).
import rclpy
from geometry_msgs.msg import PoseArray
from . import class_base as bc

from .Tracking import ModuleTracking as mT
from .Tracking.common import utilsImage as uImage
from .ROV import utilsRos as uRos


class ImageTracker(bc.BaseRos2):

    selected_points:PoseArray = None
    frame = None
    cv_bridge = CvBridge()
    vt:mT.VisualTracking

    def __init__(self, rclpy=rclpy, name="Image Tracking class", frequency=30):
        super().__init__(rclpy=rclpy, name=name, frequency=frequency)
        self.vt = mT.VisualTracking(self)
        

    def run_parameters(self):
        super().run_parameters()
        self.declare_parameter("param_show_image", False)
        self.declare_parameter("param_show_mask", False)

        self.declare_parameter("param_roi_factor", 2)
        self.declare_parameter("param_img_threshold", 254)


    
    def run_publishers(self):
        super().run_publishers()
        self.publisher_pts_tracked = self.create_publisher(PoseArray, '/IBVS/image/detected/meter', 10) 
        self.publisher_pts_tracked_center = self.create_publisher(PoseArray, '/IBVS/image/detected/center', 10) 
        self.publisher_pts_tracked_raw = self.create_publisher(PoseArray, '/IBVS/image/detected/raw', 10) 
        self.publisher_mask = self.create_publisher(Image, "/IBVS/image/debug/mask", 10)
        self.publisher_mask_colored = self.create_publisher(Image, "/IBVS/image/debug/mask/colored", 10)


    def run_subscribers(self):
        super().run_subscribers()
        self.subscriber_image = self.create_subscription(Image, "/IBVS/sensor/camera", self.__callback_on_frame, 10)
        self.subscriber_selected_points = self.create_subscription(PoseArray, "/IBVS/image/selected/raw", self.__callback_on_selected_points, 10)


    def update(self):
        if self.frame is not None:
            self.vt._image_base(self.frame.copy(), self.param_roi_factor, self.param_img_threshold)
            if self.param_show_image and self.param_debug:
                uImage.show_image(self.frame, name="image", timeout=1000)

            self.frame = None


    def __callback_on_frame(self, data):
        self.log("info", "Frame received")
        cv_image = self.cv_bridge.imgmsg_to_cv2(data)
        self.frame = cv_image        


    def __callback_on_selected_points(self, data):
        pts = uRos.poseArray_to_points(data)
        self.selected_points = pts
        self.vt.pts_hand_selected = pts
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
        elif topic == "Tracking/points/center":
            self.log("info", f"Publsihing : {msg}")
            self.publisher_pts_tracked_center.publish(msg)
        elif topic == "Tracking/points/raw":
            self.log("info", f"Publsihing : {msg}")
            self.publisher_pts_tracked_raw.publish(msg)
        elif topic == "Tracking/mask/colored":
            self.log('info', "on mask")
            if self.param_debug == True:
                self.publisher_mask_colored.publish(msg)
            if self.param_show_mask and self.param_debug:
                uImage.show_image(data, name="mask colored")
        elif topic == "Tracking/mask":
            self.log('info', "on mask")
            if self.param_debug:
                self.publisher_mask.publish(msg)
            if self.param_show_mask and self.param_debug:
                uImage.show_image(data, name="mask")

def main(argv=None):
    rclpy.init(args=argv)
    blueRov = ImageTracker(frequency=30, name="Tracker", rclpy=rclpy)
    blueRov.node_run()

if __name__ == '__main__':
    main()
