#!/usr/bin/env python

# rgb detection
import numpy as np

def rgb_detection(rgb,color='r'):
	if color not in ('r','b','y','g'):
		print "You need to choose red, blue, yellow, or green."
		return []

	# getting each columns
	r,g,b = np.rollaxis(data,axis=-1)
	# new array 3d, filled with zeros (black)
    result = np.zeros(data.shape[:3],dtype=np.uint8)
    
    # boundaries [b,g,r]
    boundaries = { 'r':([17, 15, 100], [50, 56, 200]),
				   'b':([86, 31, 4], [220, 88, 50]),
				   'y':([25, 146, 190], [62, 174, 250]),
				   'g':([103, 86, 65], [145, 133, 128])}
	# get lower and upper bound
	lower,upper = boundaries[color]
	# get true or false 2d array
    mask = (b >= lower[0]) & (b <= upper[0]) & (g >= lower[0]) & (g <= upper[0]) & (r >= lower[2]) & (r <= upper[2])
    # if true, fill with white 
    result[mask] = [255,255,255]

    return result