#!/usr/bin/env python3
import rclpy
from sensor_msgs.msg import Image #new This line imports the ROS 2 message type 
from cv_bridge import CvBridge  #new converting between ROS Image messages and OpenCV images (numpy arrays).
from geometry_msgs.msg import PoseArray
import IBVS_ROV.Utils.ROS.class_base as bc
from rclpy.qos import QoSProfile, QoSReliabilityPolicy, QoSHistoryPolicy
from std_msgs.msg import Header

import IBVS_ROV.Tracking.Module.selection as mS
import IBVS_ROV.Utils.ROS.utilsMessage as uMessage

class PointsSelection(bc.BaseRos2):

    image = None
    tracker:mS.VisualTracking
    cv_bridge = CvBridge()

    def __init__(self, node_rclpy, name="selecter", frequency=30):
        super().__init__(frequency=frequency, 
                         node_rclpy=node_rclpy,
                         name_app=name
                         )
        self.log("info", "Init Points Selection object")
        self.tracker = mS.VisualTracking(self)


    def run_subscribers(self):
        super().run_subscribers()
        qos_profile = QoSProfile(
            reliability=QoSReliabilityPolicy.BEST_EFFORT,
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=1
        )
        self.subscriber_image = self.create_subscription(Image, "sensor/camera", self._callback_on_frame, qos_profile, namespace_override=True)


    def run_publishers(self):
        super().run_publishers()
        self.publisher_pts_selected_raw = self.create_publisher(PoseArray, 'image/selected/raw', 10, namespace_override=True) 

    def run_parameters(self):
        super().run_parameters()


    def update(self):
        
        if (self.image is not None):
            image = self.image
            self.log("info", "Selecting points on an image")
            self.tracker.is_selecting = True
            try:
                self.tracker.select_points(image)
            except ValueError as e:
                self.log("error", f"Not enough points : {str(e)}")
            
    
    def _callback_on_frame(self, image):
        cv_image = self.cv_bridge.imgmsg_to_cv2(image)
        self.image = cv_image


    def publish(self, topic, data, verbose):
        msg = uMessage.points_to_poseArray(data)
        self.log("debug", f"Topic : {topic}, data : {msg}")

        header = Header()
        header.stamp = self.get_clock().now().to_msg()
        msg.header = header

        if "points/raw" in topic:
            self.publisher_pts_selected_raw.publish(msg)


    
def main(argv=None):
    rclpy.init(args=argv)
    blueRov = PointsSelection(frequency=30, name="BlueRov", node_rclpy=rclpy)
    blueRov.node_run()

if __name__ == '__main__':
    main()

    