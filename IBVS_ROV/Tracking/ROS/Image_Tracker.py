#!/usr/bin/env python3
import cv2
from sensor_msgs.msg import Image #new This line imports the ROS 2 message type 
from cv_bridge import CvBridge  #new converting between ROS Image messages and OpenCV images (numpy arrays).
import rclpy
from geometry_msgs.msg import PoseArray
import IBVS_ROV.Utils.ROS.class_base as bc

import IBVS_ROV.Tracking.Module.detection as mD

import IBVS_ROV.Utils.ROS.utilsMessage as uMessage
from rclpy.qos import QoSProfile, QoSReliabilityPolicy, QoSHistoryPolicy


class ImageTracker(bc.BaseRos2):

    selected_points:PoseArray = None
    frame = None
    cv_bridge = CvBridge()
    vt:mD.VisualTracking

    def __init__(self, rclpnode_rclpyy=rclpy, name="tracker", frequency=30):
        super().__init__(frequency=frequency, 
                         node_rclpy=rclpy,
                         name_app=name
                         )
        self.vt = mD.VisualTracking(self)
        

    def run_parameters(self):
        super().run_parameters()
        self.declare_parameter("param_show_image", False)
        self.declare_parameter("param_show_mask", False)

        self.declare_parameter("param_roi_factor", 2)
        self.declare_parameter("param_img_threshold", 254)


    
    def run_publishers(self):
        super().run_publishers()
        qos_profile = QoSProfile(
            reliability=QoSReliabilityPolicy.BEST_EFFORT,
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=1
        )
        self.publisher_pts_tracked_raw = self.create_publisher(PoseArray, 'image/detected/raw', qos_profile, namespace_override=True) 
        self.publisher_mask = self.create_publisher(Image, "image/debug/mask/raw", qos_profile, namespace_override=True)
        self.publisher_mask_colored = self.create_publisher(Image, "image/debug/mask/colored", qos_profile, namespace_override=True)



    def run_subscribers(self):
        qos_profile = QoSProfile(
            reliability=QoSReliabilityPolicy.BEST_EFFORT,
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=1
        )
        super().run_subscribers()
        self.subscriber_image = self.create_subscription(Image, "sensor/camera", self.__callback_on_frame, qos_profile, namespace_override=True)
        self.subscriber_selected_points = self.create_subscription(PoseArray, "image/selected/raw", self.__callback_on_selected_points, qos_profile, namespace_override=True)


    def _handle_image(self, image):
        self.vt.detect_points(image, roi_factor=self.param_roi_factor, img_threshold=self.param_img_threshold)

    def update(self):
        if self.frame is not None:
            try:
                self._handle_image(self.frame)
            except ValueError as e:
                if self.param_debug :
                    self.log("error", f"Value error : {str(e)}")
            self.frame = None


    def __callback_on_frame(self, data):
        cv_image = self.cv_bridge.imgmsg_to_cv2(data)
        self.frame = cv_image   


    def __callback_on_selected_points(self, data):
        pts = uMessage.poseArray_to_points(data)
        self.selected_points = pts
        self.vt.pts_hand_selected = pts
        self.vt.pts_old_selected = self.selected_points


    def publish(self, topic, data, verbose):
        msg = None
        if "points" in topic:
            msg = uMessage.points_to_poseArray(data)
        elif 'mask' in topic:
             msg = self.cv_bridge.cv2_to_imgmsg(data, "rgb8")        
        else: 
            raise TypeError('The topic name should at least contains points or mask')
        if topic == "points/raw":
            self.publisher_pts_tracked_raw.publish(msg)
        elif topic == "mask/annotated":
            if self.param_debug == True:
                self.publisher_mask_colored.publish(msg)
        elif topic == "mask":
            if self.param_debug:
                self.publisher_mask.publish(msg)

def main(argv=None):
    rclpy.init(args=argv)
    blueRov = ImageTracker(frequency=30, name="Tracker", node_rclpy=rclpy)
    blueRov.node_run()

if __name__ == '__main__':
    main()
