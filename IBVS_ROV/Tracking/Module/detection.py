# import interface as iface
import IBVS_ROV.Tracking.Module.Image.utilsImage as uImage
import IBVS_ROV.Tracking.Module.Image.utilsCv2 as uCV2
import IBVS_ROV.Tracking.Module.Image.utilsRoi as uRoi
import IBVS_ROV.Tracking.Module.Image.utilsTracking as uTracking
import cv2


class VisualTracking:

    interface = None
    is_selecting:bool = False
    pts_old_selected = None

    def __init__(self, interface):
        self.interface = interface

    


    def detect_points(self, frame, roi_factor=1.3, img_threshold=250):
        """
        Output : Mask colored : 
        - Green : points non sorted
        - Red : Points selected
        - Blue Points kept for error
        """

        # Detecting keypoints : 
        pts_new, mask = uTracking.generate_keypoints(frame, bot_threshold=img_threshold)
        mask_colored = cv2.cvtColor(mask, cv2.COLOR_GRAY2RGB)
        mask_colored = uCV2.draw_points(mask_colored, pts_new, [0,255,0])

        self.interface.publish("mask",mask_colored,verbose="notset")

        if self.pts_old_selected is None:
            return False
        if (len(pts_new) < 4):
            return False

        # Generation ROI
        roi, mask_colored = uRoi.roi_generate(mask_colored, self.pts_old_selected, True, factor=roi_factor)
        mask_colored = uImage.draw_points(mask_colored, self.pts_hand_selected, [255,0,0])
        if (roi != None):
            pts_new_selected = uRoi.roi_select_points(roi, pts_new)
            _, board_points = uTracking.order_points(pts_new_selected)

            # Drawing on image
            mask_colored = uCV2.draw_points(mask_colored, board_points, (0, 0, 255))
            mask_colored = uCV2.draw_text_points(mask_colored, board_points)
            # mask_colored = utilsImage.draw_points(mask_colored, self.pts_old_selected, (255,0,0))

            self.interface.publish("mask/annotated",mask_colored,verbose="notset")
            if (len(board_points) != 5) :
                raise ValueError("Nb of points incorrect")

            self.pts_old_selected = board_points
            # publishing all data : 
            
            self.interface.publish("points/raw", board_points, "debug")
        else:
            self.interface.publish("mask/annotated",mask_colored,verbose="notset")
