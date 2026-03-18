import rclpy
import rclpy.timer
from rclpy.node import Node
from std_msgs.msg import Header
from datetime import datetime
import traceback
import rclpy.logging
from rclpy.publisher import Publisher
import time

from rclpy.qos import QoSProfile, QoSReliabilityPolicy, QoSHistoryPolicy



class BaseRos2(Node):
    dT:float
    name:str
    timer_update:rclpy.timer.Timer
    local_rclpy:rclpy
    name_space:str = None
    name_app:str = None

    loop_time_start:float


    

    def __init__(self, node_rclpy:rclpy, name_app, name_space="IBVS", frequency=30):
        super().__init__(name_app)
        self.dT = 1/frequency
        self._log = self.get_logger()
        self.local_rclpy = node_rclpy
        self.name_space = name_space
        self.name_app = name_app

        self.qos_profile = QoSProfile(
            reliability=QoSReliabilityPolicy.RELIABLE,
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=5
        )

        self.run_parameters()
        self.run_subscribers()
        self.run_publishers()
        self.set_state("starting")
        

    def __enter__(self):
        self.log("info", "------ Method : Enter")
        obj = self.enter()
        self.log("info", "------ Starting ROS")
        self.set_state("started")
        if self.param_loop_mode:
            self.loop_time_start = 0            
        else:
            self.timer_update = self.create_timer(self.dT, self._update)
        
        return obj

    def __exit__(self, exc_type=None, exc=None, tb=None):
        self.timer_update.cancel()
        self.log("info", "------ Method : Exit")
        self.exit()
        # ROS call : 
        self.destroy_node()
        self.local_rclpy.shutdown()

    def __getattr__(self, name):
        # Function which get called when attribute not found
        try:
            value = self.get_parameter(name).value
            return value
        except Exception as e:
            raise KeyError(f"Element not found : {name} either in object or in parameters {str(e)}")
        
    def create_publisher(self, msg_type, topic, qos_profile, *, 
                            namespace_override = False,
                            callback_group = None,
                            event_callbacks = None,
                            qos_overriding_options = None,
                            publisher_class = Publisher):
        if type(namespace_override) == str:
            # Case where namespace override is str
            topic = f"/{namespace_override}/{topic}"
            
        if namespace_override == True and self.name_space is not None:
            topic = f"/{self.name_space}/{topic}"
        return super().create_publisher(msg_type, topic, qos_profile, callback_group=callback_group, event_callbacks=event_callbacks, qos_overriding_options=qos_overriding_options, publisher_class=publisher_class)
    
    def create_subscription(self, msg_type, topic, callback, qos_profile, *, namespace_override = False, callback_group = None, event_callbacks = None, qos_overriding_options = None, raw = False):
        if type(namespace_override) == str:
            # Case where namespace override is str
            topic = f"/{namespace_override}/{topic}"
            
        if namespace_override == True and self.name_space is not None:
            topic = f"/{self.name_space}/{topic}"

        return super().create_subscription(msg_type, topic, callback, qos_profile, callback_group=callback_group, event_callbacks=event_callbacks, qos_overriding_options=qos_overriding_options, raw=raw)

    def run_subscribers(self):
        pass

    def run_publishers(self):
        self.pub_state = self.create_publisher(Header, f"state/{self.name_app}", qos_profile=self.qos_profile, namespace_override=True)

    def run_parameters(self):
        self.declare_parameter('param_debug', True)
        self.declare_parameter("param_log_min_level", rclpy.logging.LoggingSeverity.DEBUG)
        self.declare_parameter("param_loop_mode", False)

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


    def _loop(self):
        tmp_time = time.time()
        if tmp_time-self.loop_time_start >= self.dT:
            self._update()
            self.loop_time_start = tmp_time
        self.local_rclpy.spin_once(self, timeout_sec=1/9000)



    def _update(self):
        self.set_state("Updating")
        self.update()
        self.set_state("Waiting")


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

        if self.param_loop_mode:
            while(self.local_rclpy.ok()):
                self._loop()

        else:

            try:
                self.local_rclpy.spin(self)
                self.__exit__()
            except Exception as e:
                self.get_logger().error(f"Error: {e}")
                self.get_logger().error(traceback.format_exc())
                self.__exit__()

    def set_state(self, state:str):
        msg = Header()
        msg.stamp = self.get_clock().now().to_msg()
        msg.frame_id = state
        if self.pub_state is not None:
            self.pub_state.publish(msg)
        else: 
            raise ValueError("Parent publisher have not been called")
        

            
        
        
        
        """try:
            self.rclpy.spin(e)
        except Exception as error:
            self.log("error", f"An error happened {str(error)}")
        finally:
            self.__exit__(None, None, None)"""



if __name__ == "__main__":
    BaseRos2.node_run()