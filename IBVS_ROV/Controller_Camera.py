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
from geometry_msgs.msg import Twist, Vector3

from .Tracking import ModuleTracking as mT
from .Tracking.common import utilsLogger as logMod
from .Tracking.common import utilsImage as uImage
from .ROV import utilsRos as uRos
from std_msgs.msg import Int16, Float32, Float64, Empty, Float32MultiArray, String
from .Tracking.common import utilsController as uCont


class CameraController(bc.BaseRos2):

    pts_selected:list[list[float]] = None
    pts_detected:list[list[float]] = None

    def __init__(self, rclpy=rclpy, frequency=30, name="Camera Controller"):
        super().__init__(rclpy=rclpy, name=name, frequency=frequency)

    def parameters(self):
        self.log("info", "Creating Parameters")
        self.declare_parameter("param_lambda", [0.3, 0.3, 0.3, 0.3, 0.3, 0.3])
        self.declare_parameter("param_attach_fab", True)


    def subscribers(self):
        self.log("info", "Creating Subscribers")
        if self.param_attach_fab == True:
            self.camera_pts_select = self.create_subscription(Float32MultiArray, "/auv/mission_planner/desired_target_pos", self.__callback_on_pts_selected, 10) # TODO dégager le /tmp 
        else:
            self.camera_pts_select = self.create_subscription(PoseArray, "/camera/points/selected/meter", self.__callback_on_pts_selected, 10) # TODO dégager le /tmp 
        if self.param_attach_fab :
            self.camera_pts_detec = self.create_subscription(Float32MultiArray, "/auv/image_computer/target_pos_px", self.__callback_on_pts_detected, 10)
        else:
            self.camera_pts_detec = self.create_subscription(PoseArray, "/camera/points/detected/meter", self.__callback_on_pts_detected, 10)
        

    def publishers(self):
        self.log("info", "Creating publishers")
        self.publisher_vel_camera = self.create_publisher(Twist, "/commande/vel/camera", 10)
        self.publisher_error_camera = self.create_publisher(PoseArray, "/commande/vel/camera/error", 10)

        self.publisher_debug_1 = self.create_publisher(Float32, "/debug_1", 10)
        self.publisher_debug_2 = self.create_publisher(Float32, "/debug_2", 10)
        self.publisher_debug_3 = self.create_publisher(Float32, "/debug_3", 10)
        

    def __callback_on_pts_selected(self, data:PoseArray):
        if self.param_attach_fab:
            self.pts_selected = uRos.multiFloat32_to_points(data)
        else:
            self.pts_selected = uRos.poseArray_to_points(data)


    def __callback_on_pts_detected(self, data:PoseArray):
        if self.param_attach_fab:
            tmp = uRos.multiFloat32_to_points(data)
        else:
            tmp = uRos.poseArray_to_points(data)
        self.pts_detected = tmp


    def _compute_error(self, target_points, actual_points):
        if (len(target_points) != len(actual_points)):
            raise ValueError("Actual points and target points cannot be differents in len")
        error = np.array(target_points) - np.array(actual_points)
        error_out = []
        for x,y,z in error:
            error_out.append([x,y])
        return error_out
    
    def __verify_z_diff_zero(self, points):
        if (points[0][2] != 0):
            return points
        list_output = []
        for i in range(len(points)):
            tmp = [points[i][0], points[i][1], 1]
            list_output.append(tmp)

        return list_output
    
    def __publish_control(self, data):
        if (np.shape(data)[0] != 6):
            raise ValueError("The shape is incorrect")
        msg = uRos.velocity_to_Twists(data)

        self.publisher_vel_camera.publish(msg)

    def __publish_error(self, data):
        msg = uRos.points_to_poseArray(data)
        self.publisher_error_camera.publish(msg)

    

    def update(self):
        if (self.pts_selected is not None) and (self.pts_detected is not None):
            self.pts_detected = self.__verify_z_diff_zero(self.pts_detected)
            self.pts_selected = self.__verify_z_diff_zero(self.pts_selected)

            pts_detected = uImage.list_points_to_meters(self.pts_detected)
            pts_selected = uImage.list_points_to_meters(self.pts_selected)

            vector_error = np.array(self._compute_error(pts_selected, pts_detected))
            matrix_L_x = uCont.construct_interaction_matrix(pts_selected)
            matrix_L_x_pinv = np.linalg.pinv(matrix_L_x)
            vector_error_flat = np.ravel(vector_error)
            matrix_ctrl = -(self.param_lambda* (matrix_L_x_pinv @ vector_error_flat))
            self.__publish_error(vector_error)
            self.__publish_control(matrix_ctrl)
            




def main(argv=None):
    rclpy.init(args=argv)
    blueRov = CameraController(frequency=30, name="Camera_Controller", rclpy=rclpy)
    blueRov.node_run()

if __name__ == '__main__':
    main()