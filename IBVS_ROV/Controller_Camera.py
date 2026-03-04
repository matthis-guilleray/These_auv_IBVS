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
from geometry_msgs.msg import Twist

from .Tracking import ModuleTracking as mT
from .Tracking.common import utilsLogger as logMod
from .Tracking.common import utilsImage as uImage
from .ROV import utilsRos as uRos
from std_msgs.msg import Int16, Float32, Float64, Empty, Float64MultiArray, String


class CameraController(bc.BaseRos2):

    pts_selected:list[list[float]] = None
    pts_detected:list[list[float]] = None

    def __init__(self, rclpy=rclpy, frequency=30, name="Camera Controller"):
        super().__init__(rclpy=rclpy, name=name, frequency=frequency)

    def parameters(self):
        self.log("info", "Creating Parameters")
        self.declare_parameter("Lambda", 0.3)


    def subscribers(self):
        self.log("info", "Creating Subscribers")
        self.camera_pts_select = self.create_subscription(PoseArray, "/camera/points/selected/raw", self.__callback_on_pts_selected, 10) # TODO dégager le /tmp 
        self.camera_pts_detec = self.create_subscription(PoseArray, "/tmp/camera/points/detected/raw", self.__callback_on_pts_detected, 10)
        

    def publishers(self):
        self.log("info", "Creating publishers")
        self.publisher_vel_camera = self.create_publisher(Twist, "/commande/vel/camera", 10)
        self.publisher_vel_camera = self.create_publisher(Twist, "/camera/points/error", 10)

        self.publisher_debug_1 = self.create_publisher(Float32, "/debug_1", 10)
        self.publisher_debug_2 = self.create_publisher(Float32, "/debug_2", 10)
        self.publisher_debug_3 = self.create_publisher(Float32, "/debug_3", 10)
        

    def __callback_on_pts_selected(self, data:PoseArray):
        self.pts_selected = uRos.poseArray_to_points(data)


    def __callback_on_pts_detected(self, data:PoseArray):
        self.pts_detected = uRos.poseArray_to_points(data)


    def _compute_error(self, target_points, actual_points):
        if (len(target_points) != len(actual_points)):
            raise ValueError("Actual points and target points cannot be differents in len")
        error = np.array(target_points) - np.array(actual_points)
        return error
    


    def update(self):
        if (self.pts_selected is not None) and (self.pts_detected is not None):
            vector_error = self._compute_error(self.pts_selected, self.pts_detected)
            self.publisher_debug_1.publish(Float32(data=vector_error[0][0]))
            self.publisher_debug_2.publish(Float32(data=vector_error[0][1]))
            self.publisher_debug_3.publish(Float32(data=vector_error[0][2]))




def main(argv=None):
    rclpy.init(args=argv)
    blueRov = CameraController(frequency=30, name="Camera_Controller", rclpy=rclpy)
    blueRov.node_run()

if __name__ == '__main__':
    main()