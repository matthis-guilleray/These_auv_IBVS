from geometry_msgs.msg import PoseArray, Pose, Point

def points_to_poseArray(points):
    msg = PoseArray()
    msg.header.frame_id = "map"

    for x, y, z in points:
        print("i")
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