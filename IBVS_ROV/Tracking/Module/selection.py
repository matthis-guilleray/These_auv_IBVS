# import interface as iface
import IBVS_ROV.Tracking.Module.Image.utilsImage as uImage
import IBVS_ROV.Tracking.Module.Image.utilsCv2 as uCV2
import IBVS_ROV.Tracking.Module.Image.utilsRoi as uRoi
import IBVS_ROV.Tracking.Module.Image.utilsTracking as uTracking
import cv2


class VisualTracking:

    interface = None

    def __init__(self, interface):
        self.interface = interface


    def select_points(self, frame):
        self.pts_hand_selected = uTracking.manually_select_keypoints(frame)
        if (len(self.pts_hand_selected) != 5):
            self.interface.log("error", "Error not enough points selected")
            return

        self.interface.publish("Tracking/pointsSelected/raw", self.pts_hand_selected, verbose="debug")