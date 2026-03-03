import cv2
import numpy as np
from . import utilsImage


def roi_increase(top_left, bot_right, factor_width, factor_height):
    width = bot_right[0] - top_left[0]
    height = bot_right[1] - top_left[1]

    width_out = width*factor_width
    height_out = height*factor_height

    out_top_left = (
        int(top_left[0] - width_out/2),
        int(top_left[1] - height_out/2)
    )
    out_bot_right = (
        int(bot_right[0] + width_out/2),
        int(bot_right[1] + height_out/2)
    )

    return out_top_left, out_bot_right


def roi_generate(mask, list_pts, draw=False, factor=1.2):
    if (len(list_pts) <= 4):
        raise ValueError(f"Not enough points : {len(list_pts)}")
    try:
        x, y, z = list(zip(*list_pts))
    except :
        x, y = list(zip(*list_pts)) # TODO faire moins bourrin

    top_left = (np.min(x), np.min(y))
    bot_right = (np.max(x), np.max(y))

    top_left_out, bot_right_out = roi_increase(top_left, bot_right, factor, factor)

    if (draw):
        cv2.rectangle(mask,top_left_out,bot_right_out,(0,255,0),3)
    roi = {
        "top_left":top_left_out,
        "bot_right":bot_right_out
    }
    return (roi, mask)

def roi_select_points(dict_roi, list_pts):
    top_left = dict_roi["top_left"]
    bot_right = dict_roi["bot_right"]

    list_output = []

    for i in list_pts:
        bool_top_left = (i[0] >= top_left[0] and i[1] >= top_left[1])
        bool_bot_right = (i[0] <= bot_right[0] and i[1] <= bot_right[1])

        if (bool_bot_right and bool_top_left):
            list_output.append(i)

    return list_output
