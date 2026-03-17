import cv2

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

def draw_text_points(image, points, text = ["tl", "bl", "c", "tr", "br"]):
    for i in range(len(points)):
        pts = [int(points[i][0])+10, int(points[i][1])+10]
        image = cv2.putText(image, text[i], pts, cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    return image

def draw_triangles(image, points):
    image = cv2.line(image, points[0], points[1], (255, 0, 0), 3)
    image = cv2.line(image, points[1], points[2], (255, 0, 0), 3)
    image = cv2.line(image, points[2], points[0], (255, 0, 0), 3)
    return image