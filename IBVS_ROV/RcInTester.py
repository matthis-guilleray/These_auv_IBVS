from . import baseClass as bc
from .Tracking.common import utilsImage
import time
import rclpy

class TestClass(bc.BaseRos2):
    def __init__(self, frequency=30):
        super(TestClass, self).__init__(frequency=frequency)

        print("Initing")
    
    def enter(self):
        print("Enter main")

    def update(self):
        print("updata")

    def exit(self):
        print("Exit")

    def enter(self):
        print("Enter")


def main(argv=None):
    rclpy.init(args=argv)
    TestClass.node_run()
    rclpy.shutdown()

if __name__ == '__main__':
    main()