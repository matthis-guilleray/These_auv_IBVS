#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
import cv2
import gi
import numpy as np
from sensor_msgs.msg import Image, PointCloud2 #new This line imports the ROS 2 message type 
from cv_bridge import CvBridge  #new converting between ROS Image messages and OpenCV images (numpy arrays).
import rclpy
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseArray, Pose, Point
from std_msgs.msg import Header
from . import class_base as bc

# import Tracking.ModuleTracking as mT
# import Tracking.common.utilsLogger as logMod


gi.require_version('Gst', '1.0')
from gi.repository import Gst

class VideoGrabber(bc.BaseRos2):
    """BlueRov video capture class constructor

    Attributes:
        port (int): Video UDP port
        video_codec (string): Source h264 parser
        video_decode (string): Transform YUV (12bits) to BGR (24bits)
        video_pipe (object): GStreamer top-level pipeline
        video_sink (object): Gstreamer sink element
        video_sink_conf (string): Sink configuration
        video_source (string): Udp source ip and port
    """

    def __init__(self):
        super().__init__(name="video", frequency=30, rclpy=rclpy)
        self.log("info", "Starting VideoGrabber")

        self.declare_parameter("port", 5600,) 
        self.declare_parameter("output_frame", False,) 
        self.declare_parameter("ros/publish", True,)

        self.declare_parameter("image_width", 1920)
        self.declare_parameter("image_height", 1080)




        self.port               = self.get_parameter("port").value
        self.output_frame  = bool(self.get_parameter("output_frame").value)
        self.ros_publish = bool(self.get_parameter("ros/publish").value)
        self.image_width = self.get_parameter("image_width").value
        self.image_height = self.get_parameter("image_height").value
        
        self._frame             = None
        self.video_source       = 'udpsrc port={}'.format(self.port)
        self.video_codec        = '! application/x-rtp, payload=96 ! rtph264depay ! h264parse ! avdec_h264'
        self.video_decode       = '! decodebin ! videoconvert ! video/x-raw,format=(string)BGR ! videoconvert'
        self.video_sink_conf    = '! appsink emit-signals=true sync=false max-buffers=2 drop=true'

        self.video_pipe         = None
        self.video_sink         = None

        # font
        self.font               = cv2.FONT_HERSHEY_PLAIN


        Gst.init() 

        # Initialize CvBridge
        self.bridge = CvBridge() # initializes an instance of CvBridge and assigns it to self.bridge. 

        # Create a publisher for the image
        self.publisher_image = self.create_publisher(Image, 'camera/image', 10) 
        #publishes messages of type Image to the topic 'bluerov2/camera/image'.(10): the queue size of the publisher.
        self._run()

    def _start_gst(self, config=None):
        """ Start gstreamer pipeline and sink
        Pipeline description list e.g:
            [
                'videotestsrc ! decodebin', \
                '! videoconvert ! video/x-raw,format=(string)BGR ! videoconvert',
                '! appsink'
            ]

        Args:
            config (list, optional): Gstreamer pileline description list
        """

        if not config:
            config = \
                [
                    'videotestsrc ! decodebin',
                    '! videoconvert ! video/x-raw,format=(string)BGR ! videoconvert',
                    '! appsink'
                ]

        command = ' '.join(config)
        self.video_pipe = Gst.parse_launch(command)
        self.video_pipe.set_state(Gst.State.PLAYING)
        self.video_sink = self.video_pipe.get_by_name('appsink0')

    @staticmethod
    def _gst_to_opencv(sample):
        """Transform byte array into np array

        Args:
            sample (TYPE): Description

        Returns:
            TYPE: Description
        """
        buf = sample.get_buffer()
        caps = sample.get_caps()
        array = np.ndarray(
            (
                caps.get_structure(0).get_value('height'),
                caps.get_structure(0).get_value('width'),
                3
            ),
            buffer=buf.extract_dup(0, buf.get_size()), dtype=np.uint8)
        return array

    def get_frame(self):
        """ Get Frame

        Returns:
            iterable: bool and image frame, cap.read() output
        """
        return self._frame

    def is_frame_available(self):
        """Check if frame is available

        Returns:
            bool: true if frame is available
        """
        return type(self._frame) != type(None)

    def _run(self):
        """ Get frame to update _frame
        """

        self._start_gst(
            [
                self.video_source,
                self.video_codec,
                self.video_decode,
                self.video_sink_conf
            ])

        self.video_sink.connect('new-sample', self.callback_on_new_sample)

    def callback_on_new_sample(self, sink):
        sample = sink.emit('pull-sample')
        new_frame = self._gst_to_opencv(sample)
        self._frame = new_frame

        return Gst.FlowReturn.OK
    
    
    def update(self):        
        if not self.is_frame_available():
            return
        frame = self.get_frame()
        width = int(self.image_width/2)#1.5
        height = int(self.image_height/2)#1.5
        dim = (width, height)
        img = cv2.resize(frame, dim, interpolation = cv2.INTER_AREA)   

        # Convert OpenCV image to ROS 2 Image message
        #This line converts the OpenCV image img (which is a numpy array) into a ROS 2 Image message (img_msg).
        #The encoding='bgr8' parameter specifies the color encoding of the image (BGR format with 8 bits per channel).
        if self.output_frame :
            cv2.imshow('BlueROV2 Camera', img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.destroy_node()

        if self.ros_publish : 
            img_msg = self.bridge.cv2_to_imgmsg(img, encoding='bgr8')
            self.publisher_image.publish(img_msg)
            
        

def main(args=None):
    rclpy.init(args=args)    
    node = VideoGrabber()
    node.node_run()

if __name__ == '__main__':
    main()
