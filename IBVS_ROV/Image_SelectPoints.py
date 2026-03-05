#!/usr/bin/env python3
import rclpy
from sensor_msgs.msg import Image #new This line imports the ROS 2 message type 
from cv_bridge import CvBridge  #new converting between ROS Image messages and OpenCV images (numpy arrays).
from geometry_msgs.msg import PoseArray
from . import class_base as bc

from .Tracking import ModuleTracking as mT
from .ROV import utilsRos as uRos

class PointsSelection(bc.BaseRos2):

    image = None
    tracker:mT.VisualTracking
    cv_bridge = CvBridge()

    def __init__(self, rclpy, name="BaseRos2", frequency=30):
        super().__init__(rclpy, name, frequency)
        self.log("info", "Init Points Selection object")
        self.tracker = mT.VisualTracking(self)


    def run_subscribers(self):
        self.subscriber_image = self.create_subscription(Image, "/IBVS/sensor/camera", self._callback_on_frame, 10)


    def run_publishers(self):
        self.publisher_pts_selected_raw = self.create_publisher(PoseArray, '/IBVS/image/selected/raw', 10) 
        self.publisher_pts_selected_center = self.create_publisher(PoseArray, '/IBVS/image/selected/center', 10) 
        self.publisher_pts_selected_meter = self.create_publisher(PoseArray, '/IBVS/image/selected/meter', 10) 


    def update(self):
        image = self.image
        if (image is not None):
            self.log("info", "Selecting points on an image")
            self.tracker.is_selecting = True
            self.tracker.on_image(image)
            
    
    def _callback_on_frame(self, image):
        self.log("info", "Frame received")
        cv_image = self.cv_bridge.imgmsg_to_cv2(image)
        self.image = cv_image
            

    def publish(self, topic, data, verbose):
        msg = uRos.points_to_poseArray(data)
        self.log("info", f"Topic : {topic}, data : {msg}")


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

    