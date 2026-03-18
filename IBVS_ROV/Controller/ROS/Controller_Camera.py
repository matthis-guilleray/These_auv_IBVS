import rclpy
import numpy as np
from geometry_msgs.msg import PoseArray
import IBVS_ROV.Utils.ROS.class_base as bc
from geometry_msgs.msg import Twist
from IBVS_ROV.Utils import utilsValue as uVal
from IBVS_ROV.Utils.ROS import utilsMessage as uMessage
from std_msgs.msg import Float32, Float32MultiArray
from IBVS_ROV.Controller.Module import utilsController as uCont
from IBVS_ROV.Tracking.Module.Image import utilsImage as uImg

from rclpy.qos import QoSProfile, QoSReliabilityPolicy, QoSHistoryPolicy



class CameraController(bc.BaseRos2):

    pts_selected:list[list[float]] = None
    pts_detected:list[list[float]] = None

    def __init__(self, rclpy=rclpy, frequency=30, name="Camera Controller"):
        super().__init__(rclpy=rclpy, name=name, frequency=frequency)

    def run_parameters(self):
        super().run_parameters()
        self.log("info", "Creating Parameters")
        self.declare_parameter("param_lambda", 0.3)
        self.declare_parameter("param_attach_fab", False)
        self.declare_parameter("param_zValue_isSet", True)
        self.declare_parameter("param_zValue_default",1)


    def run_subscribers(self):
        super().run_subscribers()

        qos_profile = QoSProfile(
            reliability=QoSReliabilityPolicy.BEST_EFFORT,
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=1
        )
        self.log("info", "Creating Subscribers")

        if self.param_attach_fab == True:
            self.camera_pts_select = self.create_subscription(Float32MultiArray, "/auv/mission_manager/desired_target_pos", self.__callback_on_pts_selected, 10) # TODO dégager le /tmp 
        else:
            self.camera_pts_select = self.create_subscription(PoseArray, "/IBVS/image/selected/raw", self.__callback_on_pts_selected, qos_profile) # TODO dégager le /tmp 
        if self.param_attach_fab :
            self.camera_pts_detec = self.create_subscription(Float32MultiArray, "/auv/image_computer/target_pos_m", self.__callback_on_pts_detected, 10)
        else:
            self.camera_pts_detec = self.create_subscription(PoseArray, "/IBVS/image/detected/raw", self.__callback_on_pts_detected, qos_profile)
        

    def run_publishers(self):
        super().run_publishers()
        self.log("info", "Creating publishers")
        self.publisher_vel_camera = self.create_publisher(Twist, "/IBVS/controller/command/camera", 10)
        self.publisher_error_camera = self.create_publisher(PoseArray, "/IBVS/controller/error/meter", 10)
        self.publisher_debug = self.create_publisher(PoseArray, "/IBVS/controller/debug2", 10)



    def update(self):
        if (self.pts_selected is not None) and (self.pts_detected is not None):
            pts_detected = self.pts_detected
            pts_selected = self.pts_selected

            matrix_ctrl, vector_error = uCont.compute_command_camera(pts_selected, pts_detected, self.param_lambda)
            self.__publish_error(vector_error)
            self.__publish_control(matrix_ctrl)
            self.__publish_debug(pts_detected)

            self.pts_detected = None
        

    def __callback_on_pts_selected(self, data:PoseArray):
        if self.param_attach_fab:
            tmp = uMessage.multiFloat32_to_points(data)
        else:
            tmp = uMessage.poseArray_to_points(data)

        tmp = uVal.handle_z_value(tmp, self.param_zValue_isSet, self.param_zValue_default)
        self.pts_selected_raw = tmp
        tmp = uImg.list_points_to_meters(tmp)
        self.pts_selected = tmp
        

    def __callback_on_pts_detected(self, data:PoseArray):
        if self.param_attach_fab:
            tmp = uMessage.multiFloat32_to_points(data)
            tmp = uVal.handle_z_value(tmp, self.param_zValue_isSet, self.param_zValue_default)
        else:
            tmp = uMessage.poseArray_to_points(data)
            tmp = uVal.handle_z_value(tmp, self.param_zValue_isSet, self.param_zValue_default)
            self.pts_detected_raw = tmp
            tmp = uImg.list_points_to_meters(tmp)
        
        self.pts_detected = tmp

    
    def __publish_control(self, data):
        if (np.shape(data)[0] != 6):
            raise ValueError("The shape is incorrect")
        msg = uMessage.velocity_to_Twists(data)

        self.publisher_vel_camera.publish(msg)

    def __publish_error(self, data):
        msg = uMessage.points_to_poseArray(data)
        self.publisher_error_camera.publish(msg)
            
    def __publish_debug(self, data:list[list[float]]):
        pArray = uMessage.points_to_poseArray(data)
        self.publisher_debug.publish(pArray)




def main(argv=None):
    rclpy.init(args=argv)
    blueRov = CameraController(frequency=60, name="Camera_Controller", rclpy=rclpy)
    blueRov.node_run()

if __name__ == '__main__':
    main()