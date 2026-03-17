import cv2
import numpy as np
import matplotlib.pyplot as plt

# TODO set this in parameters
cam_info_width = 640
cam_info_height = 480
fx = 525
cam_info_k = [ 525, 0.0, cam_info_width/2,
               0.0, 525, cam_info_height/2,
               0.0, 0.0, 1.0]
cam_info_d = [0.0, 0.0, 0.0, 0.0, 0.0]
cam_info_r = [1.0, 0.0, 0.0,
              0.0, 1.0, 0.0,
              0.0, 0.0, 1.0]
cam_info_p = [525, 0.0, cam_info_width/2, 0.0,
            0.0, 525, cam_info_height/2, 0.0,
            0.0, 0.0, 1.0, 0.0]



def extract_channel(image, channel=1):
    output_channel = image[:,:,channel]
    return output_channel

def pixel_to_meters(u, v, z):
    fx = cam_info_k[0] # lx
    fy = cam_info_k[4] # ly
    cx = cam_info_k[2] # u0
    cy = cam_info_k[5] # v0

    x = (u - cx) * z / fx
    y = (v - cy) * z / fy
    return [x, y, z]

def list_points_to_meters(list_points):
    out_list = []
    for point in list_points:
        if len(point) != 3:
            raise ValueError(f"Point length is different of 3 : {len(point)}")
        out_list.append(pixel_to_meters(point[0], point[1], point[2]))

    return out_list
