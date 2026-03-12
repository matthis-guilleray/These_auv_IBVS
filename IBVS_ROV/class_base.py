import rclpy
import rclpy.timer
from rclpy.node import Node
from datetime import datetime
import traceback
import rclpy.logging



class BaseRos2(Node):
    dT:float
    name:str
    timer_update:rclpy.timer.Timer
    rclpy:rclpy

    def __init__(self, rclpy, name="BaseRos2", frequency=30, namespace="", app_name=""):
        super().__init__(name)
        self.dT = 1/frequency
        self._log = self.get_logger()
        self.rclpy = rclpy
        self.namespace = namespace
        self.app_name = app_name
        self.run_parameters()
        self.run_subscribers()
        self.run_publishers()
        
        self.timer_update = self.create_timer(self.dT, self.update)

        

    def __enter__(self):
        self.log("info", "------ Method : Enter")
        obj = self.enter()
        self.log("info", "------ Starting ROS")
        return obj

    def __exit__(self, exc_type=None, exc=None, tb=None):
        self.timer_update.cancel()
        self.log("info", "------ Method : Exit")
        self.exit()
        # ROS call : 
        self.destroy_node()
        self.rclpy.shutdown()

    def __getattr__(self, name):
        # Function which get called when attribute not found
        try:
            value = self.get_parameter(name).value
            return value
        except Exception as e:
            raise KeyError(f"Element not found : {name} either in object or in parameters {str(e)}")

    def run_subscribers(self):
        pass

    def run_publishers(self):
        pass

    def run_parameters(self):
        self.declare_parameter('param_debug', True)
        self.declare_parameter("param_log_min_level", rclpy.logging.LoggingSeverity.DEBUG)

    def log(self, log_level, data, once = False, skip_first = False):
        once = False
        skip_first = False
        now = datetime.now()
        f = now.strftime("%m-%d - %H:%M:%S.%f")
        text = f"{f} - {str(data)}"
        self.get_logger().set_level(self.param_log_min_level)

        match log_level:
            case "notset":
                pass
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
        pass

    def exit(self):
        pass

    def enter(self):
        pass

    def node_run(self):
        # rclpy.init(args=args)
        self.__enter__()
        # context.on_shutdown(self.__exit__)
        try:
            self.rclpy.spin(self)
            self.__exit__()
        except Exception as e:
            self.get_logger().error(f"Error: {e}")
            self.get_logger().error(traceback.format_exc())
            self.__exit__()
        

            
        
        
        
        """try:
            self.rclpy.spin(e)
        except Exception as error:
            self.log("error", f"An error happened {str(error)}")
        finally:
            self.__exit__(None, None, None)"""



if __name__ == "__main__":
    BaseRos2.node_run()