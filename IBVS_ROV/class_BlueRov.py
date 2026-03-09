import rclpy
from rclpy.qos import QoSProfile, QoSReliabilityPolicy, QoSHistoryPolicy
from std_msgs.msg import Int16, Float64
from sensor_msgs.msg import Joy, Imu, FluidPressure, LaserScan
from mavros_msgs.msg import OverrideRCIn
from sensor_msgs.msg import BatteryState
from geometry_msgs.msg import Twist
from . import class_base as bc
from .ROV import communication as cmBR
from .ROV import utilsValue as uVal 

QOS_PROFILE = 10
BP_ARM = 7 # Start bp
BP_DISARM = 6 # Back bp
BP_MANUAL = 3 # Y bp
BP_AUTOM = 2 # X bp
BP_NEUTRAL = 0 # A button = 0
BP_MAX_INDEX = 7




class BlueRov(bc.BaseRos2):

    status_arm_logic = None
    status_arm_real = False

    supress_battery_warning = False

    mode_requested = {
        "robot_arm":False,
        "robot_disarm":False,
        "control_manual":True,
        "control_autom":False,
        "control_neutral":False
    }
    



    def __init__(self, rclpy, frequency_main, name):
        super(BlueRov, self).__init__(rclpy=rclpy, frequency=frequency_main, name=name, namespace="/bluerov2")
        if (self.param_ignore_arm == False):
            self.client_arming = cmBR.blueRov_create_client(self)
            cmBR.set_disarm(self, self.client_arming)
            cmBR.set_stream_rate(self, 25)
        self.app_name = "IBVS"


    def enter(self):
        """
        Super function called on node startup
        """
        pass

    
    def exit(self):
        """
        Super function called on node stop
        """
        if self.param_ignore_arm == False:
            cmBR.set_disarm(self, self.client_arming)
        self.log("info", "Ending RosPin")


    def update(self):
        """
        Super function called on a timer of frequency_main
        """
        if self.param_stop == True:
            cmBR.set_override_rcin_neutral(self)
            self.mode_requested["robot_disarm"] = True

        if self.mode_requested["robot_arm"] == True and self.status_arm_logic == False:
            if self.param_ignore_arm == False:
                cmBR.set_arm(self, self.client_arming)

            self.mode_requested["robot_disarm"] = False
            self.mode_requested["robot_arm"] = False

        if self.mode_requested["robot_disarm"] == True:
            if self.param_ignore_arm == False:
                cmBR.set_disarm(self, self.client_arming)
            self.mode_requested["robot_disarm"] = False
            self.mode_requested["robot_arm"] = False

        if self.mode_requested["control_neutral"] == True:
            cmBR.set_override_rcin_neutral(self)

        if self.status_arm_logic is None:
            self.status_arm_logic = self.status_arm_real
            self.log("warning", f"Arming status : {self.status_arm_real}")


    def run_subscribers(self):
        super().run_subscribers()
        qos_profile = QoSProfile(
            reliability=QoSReliabilityPolicy.BEST_EFFORT,
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=1
        )
        self.log("info", "joy : " + self.namespace+"/joy")
        self.subscriber_joystick = self.create_subscription(Joy, self.namespace+"/joy", self._callback_set_cmd_bp, qos_profile=qos_profile)
        self.subscriber_cmdvel = self.create_subscription(Twist, self.namespace+"/cmd_vel", self._callback_cmd_manual_vel, qos_profile=qos_profile)
        self.subscriber_imu = self.create_subscription(Imu, self.namespace+"/imu/data", self._callback_imu, qos_profile=qos_profile)
        self.subscriber_battery = self.create_subscription(BatteryState, self.namespace+"/battery", self._callback_battery, 
                                                           qos_profile=QoSProfile(reliability=QoSReliabilityPolicy.BEST_EFFORT, 
                                                                                  history=QoSHistoryPolicy.KEEP_LAST, 
                                                                                  depth=1))
        self.create_subscription(Twist, "/"+self.app_name+"/controller/command/robot", self.__callback_cmd_vel_robot, qos_profile)


    def run_publishers(self):
        self.publisher_override_rc_in = self.create_publisher(OverrideRCIn, self.namespace+"/rc/override", QOS_PROFILE)
        self.publisher_angle_degrees = self.create_publisher(Twist, self.namespace+'/angle_degree', QOS_PROFILE)
        self.publisher_depth = self.create_publisher(Float64, self.namespace+'/depth', QOS_PROFILE)
        self.publisher_angular_velocity = self.create_publisher(Twist, self.namespace+'/angular_velocity', QOS_PROFILE)
        self.publisher_linear_velocity = self.create_publisher(Twist, self.namespace+'/linear_velocity', QOS_PROFILE)


    def run_parameters(self):
        super().run_parameters()
        self.declare_parameter("param_battery_min_warn", 15.3)
        self.declare_parameter("param_battery_min_fail", 14.0)
        self.declare_parameter("param_gain_global", 1.0)
        self.declare_parameter("param_gain_vx", 1.0)
        self.declare_parameter("param_gain_vy", 1.0)
        self.declare_parameter("param_gain_vz", 1.0)
        self.declare_parameter("param_gain_rx", 1.0)
        self.declare_parameter("param_gain_ry", 1.0)
        self.declare_parameter("param_gain_rz", 1.0)
        self.declare_parameter("param_stop", False)
        self.declare_parameter("param_ignore_arm", True)

        
        self.declare_parameter('param_neutral', 1500)

        self.declare_parameter('param_pwm_max', 1900)
        self.declare_parameter('param_pwm_min', 1100)



    def joystick_is_mode_manual(self):
        return self.mode_requested["control_manual"]
    

    def joystick_is_automatic(self):
        return self.mode_requested["control_autom"]
    

    def _callback_set_cmd_bp(self, data):
        if data.buttons[BP_ARM] == 1 :
            self.log("info", "Arming")
            self.mode_requested["robot_arm"] = True
            self.mode_requested["robot_disarm"] = False
        if data.buttons[BP_DISARM] == 1:
            self.log("info", "Disarming")
            self.mode_requested["robot_disarm"] = True
            self.mode_requested["robot_arm"] = False

        if data.buttons[BP_MANUAL] == 1:
            self.log("info", "Manual")
            self.mode_requested["control_manual"] = True
            self.mode_requested["control_autom"] = False
        if data.buttons[BP_AUTOM] == 1:
            self.log("info", "Autom")
            self.mode_requested["control_manual"] = False
            self.mode_requested["control_autom"] = True
        
        self.mode_requested["control_neutral"] = data.buttons[BP_NEUTRAL]
        
    
    def _callback_cmd_manual_vel(self, cmd_vel):
        if bool(self.joystick_is_mode_manual()):
            self.set_twist(cmd_vel)

    def set_twist(self, cmd_vel:Twist):
        # Extract cmd_vel message
        roll_left_right = self._map_value(cmd_vel.angular.x, self.param_gain_rx)
        yaw_left_right = self._map_value(cmd_vel.angular.z, self.param_gain_rz)
        ascend_descend = self._map_value(cmd_vel.linear.z, self.param_gain_vz)
        forward_reverse = self._map_value(cmd_vel.linear.x, self.param_gain_vx)
        lateral_left_right = self._map_value(cmd_vel.linear.y, self.param_gain_vy)
        pitch_left_right = self._map_value(cmd_vel.angular.y, self.param_gain_ry)

        cmBR.set_override_rcin(self, pitch_left_right, roll_left_right, ascend_descend, yaw_left_right, forward_reverse,
                             lateral_left_right)      

    def _map_value(self, value, gain):
        return uVal.map_value_scale(value, gain=gain*self.param_gain_global, neutral=self.param_neutral, scale=self.param_neutral - self.param_pwm_min)

    def _callback_cmd_automatic_vel(self, cmd_vel:Twist):
        if (self.joystick_is_automatic()):
            self.set_twist(cmd_vel)

    def _callback_battery(self, battery:BatteryState):
        if battery.voltage <= self.param_battery_min_fail:
            self.log("error", f"Battery Error : too low : voltage : {battery.voltage}")
            raise SystemError(f"Battery error : {battery.voltage}v")
        elif battery.voltage <= self.param_battery_min_warn and self.supress_battery_warning == False :
            self.log("warning", f"Battery warning : voltage : {battery.voltage}")
            self.supress_battery_warning = True
        

    def _callback_imu(self, data):
        pass


def main(argv=None):
    rclpy.init(args=argv)
    blueRov = BlueRov(frequency_main=30, name="BlueRov", rclpy=rclpy)
    blueRov.node_run()

if __name__ == '__main__':
    main()