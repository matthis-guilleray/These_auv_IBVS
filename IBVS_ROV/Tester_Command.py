from . import class_BlueRov as br
from .ROV import communication as cmBr
import rclpy
from geometry_msgs.msg import Twist
from .ROV import utilsRos as uRos
from .ROV import utilsValue as uVal 

class TesterCommand(br.BlueRov):

    def __init__(self, rclpy, frequency_main, name):
        super().__init__(rclpy, frequency_main, name)


    def run_parameters(self):
        super().run_parameters()
        self.declare_parameter('param_topic_test_camera', "/IBVS/controller/command/camera")
        self.declare_parameter('param_topic_test_robot', "/IBVS/controller/command/robot")


    def run_publishers(self):
        super().run_publishers()
        self.publisher_topic_camera = self.create_publisher(Twist, self.param_topic_test_camera, 10)     


    def run_subscribers(self):
        super().run_subscribers()
        self.create_subscription(Twist, self.param_topic_test_robot, self._callback_cmd_automatic_vel, 10)
        

    def _callback_cmd_manual_vel(self, cmd_vel:Twist):
        # Extract cmd_vel message
        super()._callback_cmd_manual_vel(cmd_vel)
        if self.joystick_is_automatic():
            self.publisher_topic_camera.publish(cmd_vel)



def main(argv=None):
    rclpy.init(args=argv)
    obj = TesterCommand(rclpy, 1, "BlueRov")
    obj.node_run()
    rclpy.shutdown()
    rclpy

if __name__ == '__main__':
    main()