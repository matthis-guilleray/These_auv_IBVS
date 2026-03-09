from . import class_BlueRov as br
from .ROV import communication as cmBr
import rclpy
import time

class RcInTester(br.BlueRov):

    channel_selected = None
    value_selected = None
    iterations = 5
    iterations_done = 5

    def run_parameters(self):
        super().run_parameters()

    def _get_int_from_keyboard(self, text):
        print("Question ", "-"*60)
        print("Ne répondre que par un nombre : ")
        data = input(text)
        if "stop" in data:

            raise KeyboardInterrupt("Stop from keyboard")
        return int(data)
    
    def enter(self):
        # cmBr.set_override_rcin_neutral(self)
        super().enter()
        return self
    
    
    def update(self):
        if self.joystick_is_automatic():
            if self.channel_selected == None:
                self.channel_selected = self._get_int_from_keyboard("Channel to test : ")
                self.log("info", f"Channel selected :  {self.channel_selected}")
            if self.channel_selected is not None and self.value_selected is None :
                self.value_selected = self._get_int_from_keyboard("Value to set : ")
                self.log("info", f"value selected :  {self.value_selected}")
                self.iterations_done = self.iterations
                self.log("info", f"Starting tests : channel : {self.channel_selected}, value : {self.value_selected}")

            if self.channel_selected is not None and self.value_selected is not None:
                cmBr.set_override_rcin_value(self, self.channel_selected, self.value_selected)
                self.iterations_done -=1
                time.sleep(0.7)
                self.log("info", self.iterations_done)

            if self.iterations_done == 0:
                cmBr.set_override_rcin_neutral(self)
                self.log("info", f"Testing done : channel : {self.channel_selected}, value : {self.value_selected}")
                self.channel_selected = None
                self.value_selected = None
            

        super().update()

    def exit(self):
        return super().exit()


def main(argv=None):
    rclpy.init(args=argv)
    obj = RcInTester(rclpy=rclpy, frequency_main=30, name="BlueRov")
    obj.node_run()
    rclpy.shutdown()
    rclpy

if __name__ == '__main__':
    main()