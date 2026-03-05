from . import class_BlueRov as br
from .ROV import communication as cmBr
import rclpy
from geometry_msgs.msg import Twist
from .ROV import utilsRos as uRos
from .ROV import utilsValue as uVal 

class TesterCommand(br.BlueRov):

    def run_parameters(self):
        super().run_parameters()
        self.declare_parameter('param_topic_test_camera', "/IBVS/controller/command/camera")
        self.declare_parameter('param_topic_test_robot', "/IBVS/controller/command/robot")


    def run_publishers(self):
        super().run_publishers()
        self.create_subscription(Twist, self.param_topic_test_robot, self.__callback_cmd_vel_robot, 10)
        


    def run_subscribers(self):
        super().run_subscribers()
        self.publisher_topic_camera = self.create_publisher(Twist, self.param_topic_test_camera, 10)

    
    def __callback_cmd_vel_robot(self, cmd_vel:Twist):
        # Extract cmd_vel message
        if (self.joystick_is_automatic()):
            self.__callback_cmd_vel_joy(cmd_vel)


    def __callback_cmd_vel_joy(self, cmd_vel:Twist):
        # Extract cmd_vel message
        super().__callback_cmd_vel_joy(cmd_vel)

        self.publisher_topic_camera.publish(cmd_vel)



def main(argv=None):
    rclpy.init(args=argv)
    obj = TesterCommand(rclpy, 1, "BlueRov", True)
    obj.node_run()
    rclpy.shutdown()
    rclpy

if __name__ == '__main__':
    main()