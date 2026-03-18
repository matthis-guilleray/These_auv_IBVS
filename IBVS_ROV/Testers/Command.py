from IBVS_ROV.Utils.BlueRov import class_BlueRov as br
import rclpy
from geometry_msgs.msg import Twist

class TesterCommand(br.BlueRov):

    """
    Could be replaced by a simple remapping of topics
    """

    def __init__(self, node_rclpy, frequency, name):

        super().__init__(frequency=frequency, 
                         node_rclpy=node_rclpy,
                         name_app=name
                         )

    def run_parameters(self):
        super().run_parameters()
        self.declare_parameter('param_topic_pub', "controller/command/camera")


    def run_publishers(self):
        super().run_publishers()
        self.publisher_topic = self.create_publisher(Twist, self.param_topic_pub, self.qos_profile, namespace_override=True)     


    def run_subscribers(self):
        super().run_subscribers()


    def _callback_cmd_manual_vel(self, cmd_vel:Twist):
        # Extract cmd_vel message
        super()._callback_cmd_manual_vel(cmd_vel)
        if self.joystick_is_automatic():
            self.publisher_topic.publish(cmd_vel)



def main(argv=None):
    rclpy.init(args=argv)
    obj = TesterCommand(rclpy, 1, "testercmd")
    obj.node_run()
    rclpy.shutdown()
    rclpy

if __name__ == '__main__':
    main()