import numpy as np


def L_x(x, y, z):
    matrix = [
        [-1/z, 0, x/z, x*y, -(1+(x*x)), y],
        [0, -1/z, y/z, 1+(y*y), -x*y, -x]
    ]
    return matrix

def construct_interaction_matrix(error):
    if (np.shape(error)[1] != 3):
        raise ValueError(f"Matrix error should be of size 3 (XYZ)")
    
    # Creating Interaction matrix
    matrix_L_x = []
    for x, y, z in error:
        matrix_L_x.append(L_x(x,y,z))
    matrix_L_x = np.reshape(matrix_L_x,(len(error)*2, 6))

    return matrix_L_x



    


