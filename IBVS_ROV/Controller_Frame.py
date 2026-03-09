import rclpy
from . import class_base as bc
from geometry_msgs.msg import Twist
from .ROV import utilsRos as uRos
from .Tracking.common import utilsController as uCont
from scipy.spatial.transform import Rotation as R
import numpy as np


class ControllerFrame(bc.BaseRos2):

    command_camera:list[float] = None

    def __init__(self, rclpy=rclpy, frequency=30, name="Frame_Controller"):
        super().__init__(rclpy=rclpy, name=name, frequency=frequency)

    def run_parameters(self):
        super().run_parameters()

        self.declare_parameter("param_rotation_order", "yxz")
        self.declare_parameter("param_rotation_value", [90, 90, 0]) # Float not allowed
        self.declare_parameter("param_translation_value_x", 0.20)
        self.declare_parameter("param_translation_value_y", 0)
        self.declare_parameter("param_translation_value_z", 0)
        

    def run_subscribers(self):
        super().run_subscribers()
        
        self.subscriber_command_camera = self.create_subscription(Twist, "/IBVS/controller/command/camera", self._callback_command_camera, 10)
        

    def run_publishers(self):
        super().run_publishers()
        self.publisher_command_robot = self.create_publisher(Twist, "/IBVS/controller/command/robot", 10)

    def update(self):
        if self.command_camera is not None:
            matrix_rotation = R.from_euler(self.param_rotation_order, self.param_rotation_value, degrees=True)
            vector_trsl = [self.param_translation_value_x, self.param_translation_value_y, self.param_translation_value_z]
            command_robot = uCont.trsf_velocity(matrix_rotation.as_matrix(), vector_trsl, self.command_camera)
            self.publisher_command_robot.publish(uRos.velocity_to_Twists(command_robot, linear_first=True))
            self.command_camera = None
            
        return super().update()
    
    def _callback_command_camera(self, data:Twist):
        self.command_camera = uRos.twist_to_velocity(data, linear_first=True)
        


def main(argv=None):
    rclpy.init(args=argv)
    blueRov = ControllerFrame(frequency=60)
    blueRov.node_run()

if __name__ == '__main__':
    main() 