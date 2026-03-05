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
    



    def __init__(self, rclpy, frequency_main, name, ignore_arm = True):
        super(BlueRov, self).__init__(rclpy=rclpy, frequency=frequency_main, name=name)
        if (ignore_arm == False):
            self.client_arming = cmBR.blueRov_create_client(self)
            cmBR.set_disarm(self, self.client_arming)
            cmBR.set_stream_rate(self, 25)
        self.ignore_arm = ignore_arm


    def enter(self):
        """
        Super function called on node startup
        """
        pass

    
    def exit(self):
        """
        Super function called on node stop
        """
        if self.ignore_arm == False:
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
            if self.ignore_arm == False:
                cmBR.set_arm(self, self.client_arming)

            self.mode_requested["robot_disarm"] = False
            self.mode_requested["robot_arm"] = False

        if self.mode_requested["robot_disarm"] == True:
            if self.ignore_arm == False:
                cmBR.set_disarm(self, self.client_arming)
            self.mode_requested["robot_disarm"] = False
            self.mode_requested["robot_arm"] = False

        if self.mode_requested["control_neutral"] == True:
            cmBR.set_override_rcin_neutral(self)

        if self.status_arm_logic is None:
            self.status_arm_logic = self.status_arm_real
            self.log("info", f"Arming status : {self.status_arm_real}")


    def run_subscribers(self):
        super().run_subscribers()
        qos_profile = QoSProfile(
            reliability=QoSReliabilityPolicy.BEST_EFFORT,
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=1
        )

        self.subscriber_joystick = self.create_subscription(Joy, "/joy", self.__callback_set_cmd_bp, qos_profile=qos_profile)
        self.subscriber_cmdvel = self.create_subscription(Twist, "/cmd_vel", self.__callback_cmd_vel_joy, qos_profile=qos_profile)
        self.subscriber_imu = self.create_subscription(Imu, "/imu/data", self.__callback_imu, qos_profile=qos_profile)
        self.subscriber_battery = self.create_subscription(BatteryState, "/battery", self.__callback_battery, 
                                                           qos_profile=QoSProfile(reliability=QoSReliabilityPolicy.BEST_EFFORT, 
                                                                                  history=QoSHistoryPolicy.KEEP_LAST, 
                                                                                  depth=1))


    def run_publishers(self):
        self.publisher_override_rc_in = self.create_publisher(OverrideRCIn, "/rc/override", QOS_PROFILE)
        self.publisher_angle_degrees = self.create_publisher(Twist, '/angle_degree', QOS_PROFILE)
        self.publisher_depth = self.create_publisher(Float64, '/depth', QOS_PROFILE)
        self.publisher_angular_velocity = self.create_publisher(Twist, '/angular_velocity', QOS_PROFILE)
        self.publisher_linear_velocity = self.create_publisher(Twist, '/linear_velocity', QOS_PROFILE)


    def run_parameters(self):
        super().run_parameters()
        self.declare_parameter("param_battery_min_warn", 16.1)
        self.declare_parameter("param_battery_min_fail", 15.9)
        self.declare_parameter("param_gain_vx", 1)
        self.declare_parameter("param_gain_vy", 1)
        self.declare_parameter("param_gain_vz", 1)
        self.declare_parameter("param_gain_rx", 1)
        self.declare_parameter("param_gain_ry", 1)
        self.declare_parameter("param_gain_rz", 1)
        self.declare_parameter("param_stop", False)



    def joystick_is_mode_manual(self):
        return self.mode_requested["control_manual"]
    

    def joystick_is_automatic(self):
        return self.mode_requested["control_autom"]
    

    def __callback_set_cmd_bp(self, data):
        self.log("info", data.buttons)
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
        
    
    def __callback_cmd_vel_joy(self, cmd_vel):
        if bool(self.joystick_is_mode_manual()):
            self.set_twist(cmd_vel)

    def set_twist(self, cmd_vel:Twist):
        # Extract cmd_vel message
        roll_left_right = uVal.map_value_scale(cmd_vel.angular.x)*self.param_gain_rx
        yaw_left_right = uVal.map_value_scale(cmd_vel.angular.z)*self.param_gain_rz
        ascend_descend = uVal.map_value_scale(cmd_vel.linear.z)*self.param_gain_vz
        forward_reverse = uVal.map_value_scale(-cmd_vel.linear.x)*self.param_gain_vx
        lateral_left_right = uVal.map_value_scale(cmd_vel.linear.y)*self.param_gain_vy
        pitch_left_right = uVal.map_value_scale(cmd_vel.angular.y)*self.param_gain_ry

        cmBR.set_override_rcin(self, pitch_left_right, roll_left_right, ascend_descend, yaw_left_right, forward_reverse,
                             lateral_left_right)


    def __callback_battery(self, battery:BatteryState):
        if battery.voltage <= self.param_battery_min_fail:
            self.log("error", f"Battery Error : too low : voltage : {battery.voltage}")
            raise SystemError(f"Battery error : {battery.voltage}v")
        elif battery.voltage <= self.param_battery_min_warn and self.supress_battery_warning == False :
            self.log("warning", f"Battery warning : voltage : {battery.voltage}")
            self.supress_battery_warning = True
        

    def __callback_imu(self, data):
        pass


def main(argv=None):
    rclpy.init(args=argv)
    blueRov = BlueRov(frequency_main=30, name="BlueRov", rclpy=rclpy)
    blueRov.node_run()

if __name__ == '__main__':
    main()