#!/usr/bin/env python3
import rclpy
from sensor_msgs.msg import Image #new This line imports the ROS 2 message type 
from cv_bridge import CvBridge  #new converting between ROS Image messages and OpenCV images (numpy arrays).
from geometry_msgs.msg import PoseArray
from . import class_base as bc
from rclpy.qos import QoSProfile, QoSReliabilityPolicy, QoSHistoryPolicy

from .Tracking import ModuleTracking as mT
from .ROV import utilsRos as uRos
from .Tracking.common import utilsTracking as uTrack

class PointsSelection(bc.BaseRos2):

    image = None
    tracker:mT.VisualTracking
    cv_bridge = CvBridge()

    def __init__(self, rclpy, name="BaseRos2", frequency=30):
        super().__init__(rclpy, name, frequency)
        self.log("info", "Init Points Selection object")
        self.tracker = mT.VisualTracking(self)


    def run_subscribers(self):
        qos_profile = QoSProfile(
            reliability=QoSReliabilityPolicy.BEST_EFFORT,
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=1
        )
        self.subscriber_image = self.create_subscription(Image, "/IBVS/sensor/camera", self._callback_on_frame, qos_profile)


    def run_publishers(self):
        self.publisher_pts_selected_raw = self.create_publisher(PoseArray, '/IBVS/image/selected/raw', 10) 
        self.publisher_pts_selected_center = self.create_publisher(PoseArray, '/IBVS/image/selected/center', 10) 
        self.publisher_pts_selected_meter = self.create_publisher(PoseArray, '/IBVS/image/selected/meter', 10) 

    def run_parameters(self):
        super().run_parameters()
        self.declare_parameter("param_points_hand_picked", False)


    def update(self):
        
        if (self.param_points_hand_picked == False):
            self.publish_pts_center()

        if (self.param_points_hand_picked and self.image is not None):
            image = self.image
            self.log("info", "Selecting points on an image")
            self.tracker.is_selecting = True
            try:
                self.tracker.on_image(image)
            except ValueError as e:
                self.log("error", f"Not enough points : {str(e)}")
            
    
    def _callback_on_frame(self, image):
        cv_image = self.cv_bridge.imgmsg_to_cv2(image)
        self.image = cv_image
            

    def publish_pts_center(self):
        pts = [
            uTrack.mire_p0,
            uTrack.mire_p1,
            uTrack.mire_p2,
            uTrack.mire_p3,
            uTrack.mire_p4]

        msg = uRos.points_to_poseArray(pts)
        self.publisher_pts_selected_meter.publish(msg)


    def publish(self, topic, data, verbose):
        msg = uRos.points_to_poseArray(data)
        self.log("debug", f"Topic : {topic}, data : {msg}")


        if "Tracking/pointsSelected/raw" in topic:
            self.publisher_pts_selected_raw.publish(msg)
        if "Tracking/pointsSelected/center" in topic:
            self.publisher_pts_selected_center.publish(msg)
        if "Tracking/pointsSelected/meter" in topic:
            self.publisher_pts_selected_meter.publish(msg)


    
def main(argv=None):
    rclpy.init(args=argv)
    blueRov = PointsSelection(frequency=30, name="BlueRov", rclpy=rclpy)
    blueRov.node_run()

if __name__ == '__main__':
    main()

    