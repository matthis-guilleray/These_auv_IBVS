from geometry_msgs.msg import PoseArray, Pose, Point, Vector3, Twist

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
        points.append([pose.position.x, pose.position.y, pose.position.z])
    return points


def velocity_to_Twists(data, linear_first=True):
    for i in range(len(data)):
        data[i] = float(data[i])
    if linear_first:
        linear = Vector3(x=data[0], y=data[1], z=data[2])
        angular = Vector3(x=data[3], y=data[4], z=data[5])
    else:
        linear = Vector3(x=data[3], y=data[4], z=data[5])
        angular = Vector3(x=data[0], y=data[1], z=data[2])

    msg = Twist(linear=linear, angular=angular)
    return msg

def twist_to_velocity(data:Twist, linear_first=True):
    if linear_first:
        velocity = [data.linear.x, data.linear.y, data.linear.z, data.angular.x, data.angular.y, data.angular.z]    
    else:
        velocity = [data.angular.x, data.angular.y, data.angular.z, data.linear.x, data.linear.y, data.linear.z]    
    return velocity

def multiFloat32_to_points(pose_array):
    points = []
    iteration = 2
    if len(pose_array.data) == 15:
        iteration = 3
    
    for i in range(0, len(pose_array.data)-(iteration-1), iteration):
        if iteration == 2:
            points.append([pose_array.data[i], pose_array.data[i+1]])
        else:
            points.append([pose_array.data[i], pose_array.data[i+1], pose_array.data[i+2]])
    return points