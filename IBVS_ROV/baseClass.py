from rclpy.node import Node
from datetime import datetime
from rclpy import get_global_executor
from rclpy.context import Context
import rclpy
import traceback



class BaseRos2(Node):
    dT:float
    name:str
    timer_update:rclpy.timer.Timer
    rclpy:rclpy

    def __init__(self, rclpy, name="BaseRos2", frequency=30):
        super().__init__(name)
        self.dT = 1/frequency
        self._log = self.get_logger()
        self.timer_update = self.create_timer(self.dT, self.update)
        self.log("info", "Hello")
        self.rclpy = rclpy
        

    def __enter__(self):
        obj = self.enter()
        self.log("info", "__enter")
        return obj

    def __exit__(self, exc_type=None, exc=None, tb=None):
        self.timer_update.cancel()
        self.log("info", "Exit base")
        self.exit()
        # ROS call : 
        self.destroy_node()

    def log(self, log_level, data, once = False, skip_first = False):
        once = False
        skip_first = False
        now = datetime.now()
        f = now.strftime("%m-%d - %H:%M:%S.%f")
        text = f"{f} - {str(data)}"

        match log_level:
            case "debug":
                self.get_logger().debug(text, once=once, skip_first=skip_first)
            case "info":
                self.get_logger().info(text, once=once, skip_first=skip_first)
            case "warning":
                self.get_logger().warning(text, once=once, skip_first=skip_first)
            case "error":
                self.get_logger().error(text, once=once, skip_first=skip_first)
            case _: 
                raise ValueError(f"Log level not found {log_level}")

    def update(self):
        raise NotImplementedError("This function should have been implemented")

    def exit(self):
        raise NotImplementedError("This function should have been implemented")

    def enter(self):
        raise NotImplementedError("This function should have been implemented")

    def node_run(self):
        # rclpy.init(args=args)
        self.__enter__()
        # context.on_shutdown(self.__exit__)
        try:
            self.rclpy.spin(self)
        except Exception as e:
            self.get_logger().error(f"Error: {e}")
            self.get_logger().error(traceback.format_exc())
            self.__exit__()
        finally:
            self.destroy_node()
        

            
        
        
        
        """try:
            self.rclpy.spin(e)
        except Exception as error:
            self.log("error", f"An error happened {str(error)}")
        finally:
            self.__exit__(None, None, None)"""



if __name__ == "__main__":
    BaseRos2.node_run()