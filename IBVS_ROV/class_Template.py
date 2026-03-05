import rclpy
from . import class_base as bc
from geometry_msgs.msg import Twist


class TemplateNode(bc.BaseRos2):

    def __init__(self, rclpy=rclpy, frequency=30, name="Frame_Controller"):
        super().__init__(rclpy=rclpy, name=name, frequency=frequency)

    def run_parameters(self):
        super().run_parameters()
        

    def run_subscribers(self):
        super().run_subscribers()
        
        self.sub_command_camera = self.create_subscription(Twist, "/commande/vel/camera", self.__callback_command_camera, 10)
        

    def run_publishers(self):
        super().run_publishers()

    def update(self):



        return super().update()
    
    def __callback_command_camera(self, data:Twist):
        pass


def main(argv=None):
    rclpy.init(args=argv)
    node = TemplateNode(frequency=60)
    node.node_run()

if __name__ == '__main__':
    main()