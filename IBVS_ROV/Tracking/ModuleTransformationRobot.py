from .common import utilsController as uCont
from . import interface as iface
import numpy as np
# from scipy.spatial.transform import RigidTransform as T
from scipy.spatial.transform import Rotation as R


class ControllerCamera:


    def __init__(self, interface):
        self.interface = interface

    def callback_on_speed_camera(self, command):
        pass


    def _generate_transformation_matrix(self):
        pass