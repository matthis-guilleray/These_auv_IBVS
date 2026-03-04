from geometry_msgs.msg import PoseArray, Pose, Point

def points_to_poseArray(points):
    msg = PoseArray()
    msg.header.frame_id = "map"


    for i in range(len(points)):
        x, y, z = points[i][0], points[i][1], 0
        if (len(points[i]) == 3):
            z = points[i][2]
        pose = Pose()
        pose.position.x = float(x)
        pose.position.y = float(y)
        pose.position.z = float(z)
        msg.poses.append(pose)

    return msg

def poseArray_to_points(pose_array):
    points = []
    for pose in pose_array.poses:
        points.append((pose.position.x, pose.position.y, pose.position.z))
    return points