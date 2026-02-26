import baseClass as bc
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




if __name__ == '__main__':
    rclpy.init(args=None)
    TestClass.node_run()
    rclpy.shutdown()