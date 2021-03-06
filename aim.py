#!/usr/bin/env python

# shape
import numpy as np
from parakeet import jit

@jit
def find_center(screen_size,points, sides):
    r,c = points.shape
    center = [0,0]
    center[1], center[0] = screen_size
    center[0] /= 2
    center[1] /= 2
    if r != 8 or c != 2 or sides < 3 or np.sum(points) == 0:
        return center

#    if sides == 3:
#        for i in xrange(8):
#            n_i = (i+1)%8
#            center[0] = abs(points[i][0] - points[n_i][0])
#            center[1] = abs(points[i][1] - points[n_i][1])
#            if center[0] > 5 or center[1] > 5:
#                n_i = (i+2)%8
#                center[0] += points[i][0] 
#                center[1] += points[i][1]
#                center[0] += abs(points[n_i][0] - center[0])/3
#                center[1] += abs(points[n_i][1] - center[1])/3
    if sides <= 4:
        center[0] = points[6][0] + (points[2][0] - points[6][0])/2
        center[1] = points[0][1] + (points[5][1] - points[0][1])/2
    else:
        center[0] = points[0][0] + (points[3][0] - points[0][0])/2
        center[1] = points[1][1] + (points[5][1] - points[1][1])/2
    return center

def get_degrees(screen_size,center):
    col,row = screen_size
    row = float(row)
    col = float(col)
    center[0] = float(center[0])
    center[1] = float(center[1])
    return (((center[0]-row/2)*(60/row)),-((center[1]-col/2)*(60/col)))
