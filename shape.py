#!/usr/bin/env python

# shape
import numpy as np
from parakeet import jit

@jit 
def find_points(bin_img):
    r,c = bin_img.shape
    # high left, left high, left low, low left, low right, right low, right high, high right
    points = np.zeros((8,2), dtype=np.int16)
    first_point_found = False
    token = False
    for i in xrange(r):
        for j in xrange(c):
            if bin_img[i,j]:
                if not first_point_found:
                    first_point_found = True
                    for ii in xrange(8):
                        points[ii][0] = i
                        points[ii][1] = j
                else:
                    if i == points[0][0] and j > points[7][1]:
                        points[7][0] = i
                        points[7][1] = j
                    if j < points[1][1]:
                        points[1][0] = i
                        points[1][1] = j
                        points[2][0] = i
                        points[2][1] = j
                    if j == points[1][1] and i > points[2][0]:
                        points[2][0] = i
                        points[2][1] = j
                    if i > points[3][0]:
                        points[3][0] = i
                        points[3][1] = j
                        points[4][0] = i
                        points[4][1] = j
                    if i == points[3][0] and j > points[4][1]:
                        points[4][0] = i
                        points[4][1] = j
                    if j > points[6][1]:
                        points[5][0] = i
                        points[5][1] = j
                        points[6][0] = i
                        points[6][1] = j
                    if j == points[6][1] and i < points[5][0]:
                        points[5][0] = i
                        points[5][1] = j
    return points

@jit
def count_sides(points):
    r,c = points.shape
    if r != 8 or c != 2:
        return -1

    sides = 0
    for i in xrange(8):
        n_i = (i+1)%8
        if (abs(points[i][0] - points[n_i][0]) + abs(points[i][1] - points[n_i][1])) > 15:
            sides += 1
    return sides
