#!/usr/bin/env python

# rgb detection
import numpy as np

def find_color(img,color='r'):
    if color not in ('r','b','y','g'):
        print "You need to choose red, blue, yellow, or green."
        return []

    # getting each columns
    r,g,b = np.rollaxis(img,axis=-1)
    
    # boundaries [b,g,r]
    boundaries = { 'r':([17, 15, 100], [50, 56, 200]),   # red
                   'b':([86, 31, 4], [220, 88, 50]),     # yellow
                   'y':([25, 146, 190], [62, 174, 250]), # blue
                   'g':([103, 86, 65], [145, 133, 128])} # gray
    # get lower and upper bound
    lower,upper = boundaries[color]
    # get true or false 2d array
    return (g >= lower[0]) & (g <= upper[0]) & (b >= lower[1]) & (b <= upper[1]) & (r >= lower[2]) & (r <= upper[2])
