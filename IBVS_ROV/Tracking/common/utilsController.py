import numpy as np


def L_x(x, y, z):
    matrix = [
        [-1/z, 0, x/z, x*y, -(1+np.sqrt(x)), y],
        [0, -1/z, y/z, 1+np.sqrt(y), -x*y, -x]
    ]
    return matrix

def construct_interaction_matrix(error):
    if (len(error) != 3):
        raise ValueError(f"Matrix error should be of size 3 (XYZ)")
    
    # Creating Interaction matrix
    matrix_L_x = [L_x(x,y,z) for x,y,z in zip(*error)]
    matrix_L_x = np.reshape(matrix_L_x,(len(error[0])*2, 6))

    return matrix_L_x



    


