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
            self.interface.log("error", "Error not enough points selected")
            return

        pts_hand_selected_ibvss = utilsImage.frame_opencv_to_ibvs(self.pts_hand_selected, utilsImage.cam_info_width, utilsImage.cam_info_height)
        pt_z = utilsTracking.estimate_target_depth(pts_hand_selected_ibvss)
        pts_z = []
        pts_x, pts_y = zip(*pts_hand_selected_ibvss)
        for i in range(len(pts_x)) : pts_z.append(pt_z)
        points = list(zip(pts_x, pts_y, pts_z))
        points_meter = utilsImage.list_points_to_meters(points)
        self.interface.publish("Tracking/pointsSelected/raw", self.pts_hand_selected, verbose="debug")
        self.interface.publish("Tracking/pointsSelected/center", points, verbose="debug")
        self.interface.publish("Tracking/pointsSelected/meter", points_meter, verbose="debug")

    


    def _image_base(self, frame, roi_factor=1.3, img_threshold=250):
        """
        Output : Mask colored : 
        - Green : points non sorted
        - Red : Points selected
        - Blue Points kept for error
        """

        # Detecting keypoints : 
        pts_new, mask = utilsTracking.generate_keypoints(frame, bot_threshold=img_threshold)
        mask_colored = cv2.cvtColor(mask, cv2.COLOR_GRAY2RGB)
        mask_colored = utilsImage.draw_points(mask_colored, pts_new, [0,255,0])

        self.interface.publish("Tracking/mask",mask_colored,verbose="notset")

        if self.pts_old_selected is None:
            return False
        if (len(pts_new) < 4):
            return False

        # Generation ROI
        roi, mask_colored = utilsRoi.roi_generate(mask_colored, self.pts_old_selected, True, factor=roi_factor)
        mask_colored = utilsImage.draw_points(mask_colored, self.pts_hand_selected, [255,0,0])
        if (roi != None):
            pts_new_selected = utilsRoi.roi_select_points(roi, pts_new)
            try:
                status, board_points = utilsTracking.order_points(pts_new_selected)
                if (status == False):
                    self.interface.log("error", f"Points : {board_points}")
            except ValueError as e: 
                self.interface.log("error", f"Value error : {str(e)}")
                return False
            board_points_ibvs = utilsImage.frame_opencv_to_ibvs(board_points, utilsImage.cam_info_width, utilsImage.cam_info_height)
            
                
            pt_z = utilsTracking.estimate_target_depth(board_points_ibvs)
            pts_x, pts_y = zip(*board_points_ibvs)
            pts_z = []
            for i in range(len(pts_x)) : pts_z.append(pt_z)
            points = list(zip(pts_x, pts_y, pts_z))
            points_meter = utilsImage.list_points_to_meters(points)

            # Drawing on image
            mask_colored = utilsImage.draw_points(mask_colored, board_points, (0, 0, 255))
            mask_colored = utilsImage.draw_text_points(mask_colored, board_points)
            # mask_colored = utilsImage.draw_points(mask_colored, self.pts_old_selected, (255,0,0))

            self.interface.publish("Tracking/mask/colored",mask_colored,verbose="notset")
            if (len(points_meter) != 5) :
                return False

            self.pts_old_selected = board_points
            # publishing all data : 
            self.interface.publish("Tracking/points/meter", points_meter, verbose="debug")  
            self.interface.publish("Tracking/points/center", board_points_ibvs, verbose="debug")
            self.interface.publish("Tracking/points/raw", board_points, "debug")
        else:
            self.interface.publish("Tracking/mask/colored",mask_colored,verbose="notset")
