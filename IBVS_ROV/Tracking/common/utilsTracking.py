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




def generate_keypoints(frame, bot_threshold=230):
    # frame = cv2.cvtColor(frameG, cv2.COLOR_BGR2GRAY)
    _, frame = cv2.threshold(frame[:,:,1],bot_threshold,255,0)
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


def find_dest(pt1, pt2):
    x1, y1 = pt1
    x2, y2 = pt2
    return math.sqrt( (x2 - x1)**2 + (y2 - y1)**2 )

def verify_ratio(tl, bl, center, tr, br):
    dest_t = find_dest(tl, tr)
    dest_b = find_dest(bl, br)
    dest_l = find_dest(tl, bl)
    dest_r = find_dest(tr, br)
    dest_tl_c = find_dest(tl, center)
    dest_bl_c = find_dest(bl, center)
    dest_tr_c = find_dest(tr, center)
    dest_br_c = find_dest(br, center)


    list_tend = []
    list_tend.append({"value":dest_t/dest_b, "obj":1, "borns":0.1}) # devrait etre égal à 1
    list_tend.append({"value":dest_l/dest_r, "obj":1, "borns":0.1}) # devrait etre égal à 1
    list_tend.append({"value":dest_tl_c/dest_bl_c, "obj":1, "borns":0.1}) # devrait etre égal à 1
    list_tend.append({"value":dest_tr_c/dest_br_c, "obj":1, "borns":0.1}) # devrait etre égal à 1
    list_tend.append({"value":dest_tl_c/dest_br_c, "obj":1.5, "borns":0.3}) # devrait etre égal à 1.5

    status = True
    for v in list_tend :
        if v["value"] > v["obj"]+v["borns"] : 
            status = False
            break
        if v["value"] < v["obj"]-v["borns"] :
            status = False
            break

    return status, list_tend





def order_points(points):


    # Unpack x and y coordinates
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]

    # Find the closest points for each extreme
    def closest_point(target_x, target_y):
        return min(points, key=lambda p: (p[0] - target_x)**2 + (p[1] - target_y)**2)

    top_left = closest_point(min(xs), min(ys))
    top_right = closest_point(max(xs), min(ys))
    bot_left = closest_point(min(xs), max(ys))
    bot_right = closest_point(max(xs), max(ys))

    # Center is the closest point to the geometric center
    center_x = (min(xs) + max(xs)) / 2
    center_y = (min(ys) + max(ys)) / 2
    center = closest_point(center_x, center_y)
    status = False
    try:
        status, _ = verify_ratio(top_left, bot_left, center, top_right, top_left)
    except :
        pass


    return status, [top_left, bot_left, center, top_right, bot_right]


"""def order_points(points):
    if (len(points) != 5):
        raise ValueError("Number of points different from expected")
    pts = np.array(points).copy()
    points.sort(key=lambda x:x[1])
    pts_tl = min(points)
    pos_br = max(points)
    center_points = points[find_center_triangle(pts)]
    pts_lu = np.
    pts_ru, pts_rd = find_right_pts(pts)

    return pts_lu, pts_ld, center_points, pts_ru, pts_rd"""


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
        return tvecs[2][0]




def compute_error(points, expected):
    """Points are ordered : 
        pts_lu, pts_ld, center_points, pts_ru, pts_rd
    Args:
        points (_type_): _description_
    """
    pass

