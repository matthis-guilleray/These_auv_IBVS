from . import baseClass as bc
from . import BlueRov as br
from .ROV import communication as cmBr
import time
import rclpy
import survey

class RcInTester(br.BlueRov):

    channel_selected = None
    value_selected = None
    iterations = 60
    iterations_done = 30

    def _get_int_from_keyboard(self, text):
        print("Question ", "-"*60)
        print("Ne répondre que par un nombre : ")
        data = input(text)
        return int(data)
    

    def update(self):

    
    def update(self):
        # if self.joystick_is_automatic():
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

        if self.iterations_done == 0:
            self.log("info", f"Testing done : channel : {self.channel_selected}, value : {self.value_selected}")
            self.channel_selected = None
            self.value_selected = None
            

        super().update()


def main(argv=None):
    rclpy.init(args=argv)
    obj = RcInTester(0.5, "Hey", True)
    obj.node_run()
    rclpy.shutdown()

if __name__ == '__main__':
    main()