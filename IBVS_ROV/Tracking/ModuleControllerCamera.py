from .common import utilsController as uCont
from . import interface as iface
import numpy as np


class ControllerCamera:

    value_lambda = 0.03
    interface:iface.NodeInterface
    points_selected = None

    def __init__(self, interface):
        self.interface = interface

    def callback_on_points_detected(self, points):
        """The value received should be : ["x":x,"y":y,"z":z]

        Args:
            dict_value (_type_): _description_
        """
        if self.points_selected == None:
            return
        if points == None:
            return
        if (len(self.points_selected) != len(points)):
            return

        speedValue = self._controller(points)

        self.interface.publish("Controller/speed/camera", speedValue)


    def callback_on_lambda(self, value_lambda):
        self.value_lambda = value_lambda

    def callback_on_points_selected(self, points):
        self.points_selected = points
        

    def _compute_error(self, target_points, actual_points):
        if (len(target_points) != len(actual_points)):
            raise ValueError("Actual points and target points cannot be differents in len")
        error = []
        for i in range(len(target_points)):
            t_x, t_y, t_z = target_points[i]
            a_x, a_y, a_z = actual_points[i]

            tmp = [
                t_x-a_x,
                t_y-a_y,
                t_z-a_z
            ]
            error.append(tmp)

        return error

    def _controller(self, points):
        if (self.points_selected == None):
            raise ValueError("No points selected")

        matrix_L_x = uCont.construct_interaction_matrix(points)
        matrix_L_x_pinv = np.linalg.pinv(matrix_L_x)
        error = self._compute_error(self.points_selected, points)
        control = -self.value_lambda * matrix_L_x_pinv @ error
        return control

    