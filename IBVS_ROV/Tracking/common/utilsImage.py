import cv2
import numpy as np
import matplotlib.pyplot as plt


"""fx = cam_info_k[0] # lx
fy = cam_info_k[4] # ly
cx = cam_info_k[2] # u0
cy = cam_info_k[5] # v0"""

cam_info_width = 1920
cam_info_height = 1080
cam_info_k = [ 455, 0.0, cam_info_width/2,
               0.0, 455, cam_info_height/2,
               0.0, 0.0, 1.0]
cam_info_d = [0.0, 0.0, 0.0, 0.0, 0.0]
cam_info_r = [1.0, 0.0, 0.0,
              0.0, 1.0, 0.0,
              0.0, 0.0, 1.0]
cam_info_p = [455, 0.0, cam_info_width/2, 0.0,
            0.0, 455, cam_info_height/2, 0.0,
            cam_info_k, 0.0, 0.0, 1.0, 0.0]


def open_video(filename):
    flux = cv2.VideoCapture(filename)  # Change to your video path
    read_video(flux)
    
    return flux


def read_video(flux:cv2.VideoCapture):
    ret, frame = flux.read()
    if not ret:
        raise TypeError("No video found")
    cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    return frame


def show_image(img, timeout=30, name="Points"):
    cv2.imshow(name, img)
    return cv2.waitKey(timeout)


def draw_keypoints(image, points:list[cv2.KeyPoint]):
    img = cv2.drawKeypoints(image,points,image,flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    return img

def draw_points(image, points:list[list[int,int]], color=(0,0,255)):
    for i in points:
        pts = [int(i[0]), int(i[1])]
        cv2.circle(image, pts, 4, color, -1)
    return image

def draw_triangles(image, points):
    image = cv2.line(image, points[0], points[1], (255, 0, 0), 3)
    image = cv2.line(image, points[1], points[2], (255, 0, 0), 3)
    image = cv2.line(image, points[2], points[0], (255, 0, 0), 3)
    return image
    

def threshold_image(image, threshold, type_th=cv2.THRESH_BINARY):
    _ , ret = cv2.threshold(image, threshold, 255, type_th)
    return ret

def histogram_image(image, percent=0.05):
    img_list = image.ravel()
    

def extract_channel(image, channel=1):
    output_channel = image[:,:,channel]
    return output_channel

def frame_opencv_to_ibvs(points, width, height):
    x,y = zip(*points)
    x = np.array(x)
    y = np.array(y)
    x = x - width / 2
    y = y - height / 2
    return list(zip(x.astype(np.int32), y.astype(np.int32)))

def pixel_to_meters(u, v, z):
    fx = cam_info_k[0] # lx
    fy = cam_info_k[4] # ly
    cx = cam_info_k[2] # u0
    cy = cam_info_k[5] # v0

    x = (u - cx) * z / fx
    y = (v - cy) * z / fy
    return int(x), int(y), int(z)

def list_points_to_meters(list_points):
    out_list = []
    for point in list_points:
        out_list.append(pixel_to_meters(point[0], point[1], point[2]))

    return out_list
