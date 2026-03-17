import numpy as np
from scipy.spatial.transform import Rotation as R


def construct_matrix_L_x(x, y, z):
    matrix = [
        [-1/z, 0, x/z, x*y, -(1+(x**2)), y],
        [0, -1/z, y/z, 1+y**2, -x*y, -x]
    ]
    return matrix

def construct_matrix_stacked_L_x(error):
    if (np.shape(error)[1] != 3):
        raise ValueError(f"Matrix error should be of size 3 (XYZ)")
    
    # Creating Interaction matrix
    matrix_L_x = []
    for x, y, z in error:
        matrix_L_x.append(construct_matrix_L_x(x,y,z))
    matrix_L_x = np.reshape(matrix_L_x,(len(error)*2, 6))

    return matrix_L_x

def construct_matrix_skew(v):
    if (len(v) != 3):
        raise ValueError(f"Matrix error, the vector should be of size 3")
    sk = np.array([
        [0,     -v[2],  v[1]],
        [v[2],  0,      -v[0]],
        [-v[1], v[0],   0]
    ])
    return sk

def contruct_matrix_adjoint(rot, sk):
    if np.shape(rot) != (3, 3):
        raise ValueError(f"Rotation Matrix shape isn't 3x3")
    if np.shape(sk) != (3,3):
        raise ValueError(f"Skew Matrix shape isn't 3x3")
    

    m1 = np.hstack((rot, rot @ sk))
    m2 = np.hstack((np.zeros((3,3)), rot))

    adj = np.vstack((m1, m2))

    return adj

def compute_error(target_points, actual_points):
    if (len(target_points) != len(actual_points)):
        raise ValueError("Actual points and target points cannot be differents in len")
    error = np.array(actual_points) - np.array(target_points)
    error_out = []
    for x,y,z in error:
        error_out.append([x,y])
    return error_out

def compute_command_camera(target_points, actual_points, param_lambda):
    vector_error = np.array(compute_error(target_points, actual_points))
    matrix_L_x = construct_matrix_stacked_L_x(actual_points)
    matrix_L_x_pinv = np.linalg.pinv(matrix_L_x)
    vector_error_flat = np.array(vector_error).flatten("C")
    matrix_ctrl = -(param_lambda* (matrix_L_x_pinv @ vector_error_flat))

    return matrix_ctrl, vector_error

def trsf_velocity(rotation:list[list[float]], translation:list[float], command:list[float]):
    if np.shape(rotation) != (3,3):
        raise ValueError(f"Rotation : Expect (3,3) not : {np.shape(rotation)}")
    if np.shape(translation) != (3,):
        raise ValueError(f"Translation : Expect (3,) not : {np.shape(translation)}")
    if np.shape(command) != (6,):
        raise ValueError(f"Command : Expect (6,) not : {np.shape(command)}")
    
    matrix_sk = construct_matrix_skew(translation)
    matrix_adjoint = contruct_matrix_adjoint(rotation, matrix_sk)
    command_robot = matrix_adjoint @ command

    return command_robot