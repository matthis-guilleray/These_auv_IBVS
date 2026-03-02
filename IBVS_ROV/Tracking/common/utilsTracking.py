import cv2
import numpy as np
from . import utilsImage
import scipy
import math

mire_p0 = np.array([0.090*10, 0.152*10, 0.000]) # Top left
mire_p1 = np.array([0.390*10, 0.154*10, 0.000]) # Bottom left
mire_p2 = np.array([0.289*10, 0.253*10, 0.000]) # Center
mire_p3 = np.array([0.092*10, 0.352*10, 0.000]) # Top left
mire_p4 = np.array([0.390*10, 0.353*10, 0.000]) # Bottom right




def generate_keypoints(frame):
    # frameG = utilsImage.extract_channel(frame, 1)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    _, frame = cv2.threshold(frame,150,255,0)
    # mask = utilsImage.threshold_image(frame, 200)

    ctrs, contours = cv2.findContours(frame, 1, cv2.CHAIN_APPROX_NONE)
    centres = []
    for i in range(len(ctrs)):
        moments = cv2.moments(ctrs[i])
        try:
            centres.append((int(moments['m10']/moments['m00']), int(moments['m01']/moments['m00'])))
            cv2.circle(frame, centres[-1], 3, (0, 50, 0), -1)
        except :
            pass


    return centres, frame


def manually_select_keypoints(img):
    
    list_points = []

    def callback_opencv_imshow(event,x,y,flags,param):
        if event == cv2.EVENT_LBUTTONDOWN:
            list_points.append([x,y])
        if event == cv2.EVENT_MBUTTONDOWN:
            list_points.clear()

    name_window = 'Points to be tracked'

    cv2.namedWindow(name_window)
    cv2.setMouseCallback(name_window,callback_opencv_imshow)
    while(1):
        img_draw = img.copy()
        utilsImage.draw_points(img_draw, list_points)
        k = utilsImage.show_image(img_draw, 10, name_window) & 0xFF

        if k == 27 :
            break
    cv2.destroyWindow(name_window)


    return list_points



def fuse_close_points(points, min_distance=20):
    """
    Fuse points that are too close (within min_distance) by replacing them with their mean.

    Args:
        points: List of (x, y) tuples.
        min_distance: Minimum distance between points to be considered separate.

    Returns:
        List of fused points.
    """
    if not points:
        return []

    fused = []
    used = [False] * len(points)

    for i, p1 in enumerate(points):
        if used[i]:
            continue
        close_points = [p1]
        for j, p2 in enumerate(points[i+1:], i+1):
            if used[j]:
                continue
            dx = p1[0] - p2[0]
            dy = p1[1] - p2[1]
            distance = math.sqrt(dx*dx + dy*dy)
            if distance < min_distance:
                close_points.append(p2)
                used[j] = True
        # Calculate mean of close points
        mean_x = int(sum(p[0] for p in close_points) / len(close_points))
        mean_y = int(sum(p[1] for p in close_points) / len(close_points))
        fused.append((mean_x, mean_y))

    return fused



def compute_triangle_area(p1, p2, p3):
	x0, y0 = p1
	x1, y1 = p2
	x2, y2 = p3
	return abs(x0*(y1 - y2) + x1*(y2 - y0) + x2*(y0 - y1)) / 2


def find_center_triangle(points):
    points = np.array(points)
    diff = points[:, None] - points[None, :]
    distances = np.sum(diff**2, axis=2).sum(axis=1)
    centre_id = np.argmin(distances)
    return centre_id


def find_left_triangle(points):

    center_index = find_center_triangle(points)
    index_p2 = center_index

    p_sctr = list(points.copy())
    p2 = np.array(p_sctr.pop(index_p2))

    # p_sctr = np.array([p0, p1, p3, p4])

    val_pts1 = 9999
    index_pts1 = 8888
    val_pts2 = 8888
    index_pts2 = 8888

    pts = scipy.spatial.distance_matrix(p_sctr, [p2])
    for i in range (len(pts)):
        if pts[i] <= val_pts1 : 
            if (pts[i] <= val_pts2):
                index_pts2 = i
                val_pts2 = pts[i]
            else:
                index_pts1 = i
                val_pts1 = pts[i]

    pts1 = np.sum(points[index_pts1])
    pts2 = np.sum(points[index_pts2])
    if (pts1 <= pts2): 
        ptsHaut = points[index_pts1]
        ptsBas = points[index_pts2]
    else:
        ptsHaut = points[index_pts2]
        ptsBas = points[index_pts1]
    return [ptsHaut, points[center_index], ptsBas]

def find_right_pts(points):

    pts_lu, pts_ld, pts_c = find_left_triangle(points)

    pts_right = list(points)
    for i in range(len(pts_right)):
        if ((pts_right[i] == pts_ld).all()):
            pts_right.pop(i)
            break

    for i in range(len(pts_right)):
        if ((pts_right[i] == pts_lu).all()):
            pts_right.pop(i)
            break
    
    for i in range(len(pts_right)):
        if ((pts_right[i] == pts_c).all()):
            pts_right.pop(i)
            break
    

    pts1 = np.sum(points[0])
    pts2 = np.sum(points[1])
    
    if (pts1 <= pts2): 
        ptsHaut = points[0]
        ptsBas = points[1]
    else:
        ptsHaut = points[1]
        ptsBas = points[0]

    return ptsHaut, ptsBas


def order_points(points):
    if (len(points) != 5):
        raise ValueError("Number of points different from expected")
    pts = np.array(points).copy()
    
    center_points = points[find_center_triangle(pts)]
    pts_lu, pts_ld, _ = find_left_triangle(pts)
    pts_ru, pts_rd = find_right_pts(pts)

    return pts_lu, pts_ld, center_points, pts_ru, pts_rd


def compute_error_xy(points, points_expected):
    pts_x, pts_y = zip(*points)
    pts_exp_x, pts_exp_y = zip(*points_expected)

    error_x = np.array(pts_x)-np.array(pts_exp_x)
    error_y = np.array(pts_y)-np.array(pts_exp_y)

    return [np.sum(error_x), np.sum(error_y)]


def estimate_target_depth(points):
    object_points = np.array(np.array([mire_p0, mire_p1, mire_p2, mire_p3, mire_p4]), dtype=np.float32)
    image_points  = np.array(points, dtype=np.float32)

    retval, _, tvecs = cv2.solvePnP(
        objectPoints=object_points,
        imagePoints=image_points,
        cameraMatrix=np.reshape(np.array(utilsImage.cam_info_k,dtype=np.float32), (3,3)),
        distCoeffs=np.array(utilsImage.cam_info_d, dtype=np.float32),
        flags=cv2.SOLVEPNP_IPPE
    )
    if retval:
        print(points)
        print(tvecs[:])
        return tvecs[2][0]




def compute_error(points, expected):
    """Points are ordered : 
        pts_lu, pts_ld, center_points, pts_ru, pts_rd
    Args:
        points (_type_): _description_
    """

