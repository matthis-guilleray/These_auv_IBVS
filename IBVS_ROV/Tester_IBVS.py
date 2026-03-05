from . import class_BlueRov as br
from .ROV import communication as cmBr
import rclpy
from geometry_msgs.msg import Twist
from .ROV import utilsRos as uRos
from .ROV import utilsValue as uVal 

class TesterIBVS(br.BlueRov):

    def run_parameters(self):
        super().run_parameters()
        


    def run_publishers(self):
        super().run_publishers()     


    def run_subscribers(self):
        super().run_subscribers()
        self.create_subscription(Twist, "/IBVS/controller/command/robot", self.__callback_cmd_vel_robot, 10)

    
    def __callback_cmd_vel_robot(self, cmd_vel:Twist):
        # Extract cmd_vel message
        if (self.joystick_is_automatic()):
            self.__callback_cmd_vel_joy(cmd_vel)




def main(argv=None):
    rclpy.init(args=argv)
    obj = TesterIBVS(rclpy, 1, "BlueRov", True)
    obj.node_run()
    rclpy.shutdown()
    rclpy

if __name__ == '__main__':
    main()