# import interface as iface
from .common import utilsImage as utilsImage
from .common import utilsRoi as utilsRoi
from .common import utilsTracking as utilsTracking
import cv2


class VisualTracking:

    interface = None
    is_selecting:bool = False
    pts_old_selected = None

    def __init__(self, interface):
        self.interface = interface

    def on_image(self, image):
        # Don't forget to change image from ros2 format to CV2 format : cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

        if (self.is_selecting):
            self._image_init(image)
        else:
            self._image_base(image)

    def on_select_asked(self, input:bool):
        """Function called when we need to manually select the keypoints

        Args:
            input (bool): _description_
        """
        self.is_selecting = input


    def _image_init(self, frame):
        self.pts_hand_selected = utilsTracking.manually_select_keypoints(frame)
        self.pts_old_selected = self.pts_hand_selected
        if (len(self.pts_hand_selected) != 5):
            self.interface.log("Error not enough points selected", "error")

        pts_hand_selected_ibvss = utilsImage.frame_opencv_to_ibvs(self.pts_hand_selected, utilsImage.cam_info_width, utilsImage.cam_info_height)
        pts_z = utilsTracking.estimate_target_depth(pts_hand_selected_ibvss)
        pts_x, pts_y = zip(*self.pts_old_selected)
        points = list(zip(pts_x, pts_y, pts_z))
        self.interface.publish("Tracking/pointsSelected", points, verbose="debug")

    


    def _image_base(self, frame):

        # Detecting keypoints : 
        pts_new, mask = utilsTracking.generate_keypoints(frame)
        pts_new_fused = utilsTracking.fuse_close_points(pts_new, 50)
        mask_colored = cv2.cvtColor(mask, cv2.COLOR_GRAY2RGB)

        self.interface.publish("Tracking/mask/colored",mask_colored,verbose="notset")
        self.interface.publish("Tracking/mask",mask,verbose="notset")

        if self.pts_old_selected is None:
            return
            raise ValueError("No points selected")

        # Generation ROI
        roi, mask_colored = utilsRoi.roi_generate(mask_colored, self.pts_old_selected, True)
        if (roi != None):
            pts_new_selected = utilsRoi.roi_select_points(roi, pts_new_fused)
            board_points = utilsTracking.order_points(pts_new_selected)
            board_points_ibvs = utilsImage.frame_opencv_to_ibvs(board_points, utilsImage.cam_info_width, utilsImage.cam_info_height)
            depth_points = utilsTracking.estimate_target_depth(board_points_ibvs)
            pts_x, pts_y = zip(*board_points_ibvs)
            points = zip(pts_x, pts_y, depth_points)
            points_meter = utilsImage.list_points_to_meters(points)

            # Drawing on image
            mask_colored = utilsImage.draw_points(mask_colored, pts_new_selected)
            mask_colored = utilsImage.draw_points(mask_colored, self.pts_hand_selected, (255,0,0))

            
            # publishing all data : 
            self.interface.publish("Tracking/points", points_meter, verbose="debug")  
            self.interface.publish("Tracking/points/ibvs_frame", board_points_ibvs, verbose="debug")
            self.interface.publish("Tracking/points/camera_frame", board_points, "debug")
