#!/usr/bin/env python
# import the relevant libraries
import numpy as np
from parakeet import jit


@jit
def dilation(bin_img, strt=3):
    r,c = bin_img.shape
    y = np.empty_like(bin_img)
    for i in xrange(r):
        for j in xrange(c):
            left_idx = max(0, i-strt/2)
            right_idx = min(r, i+strt/2+1)
            currmax = bin_img[left_idx, j]
            for ii in xrange(left_idx+1, right_idx):
                elt = bin_img[ii, j]
                if elt > currmax:
                    currmax = elt
            y[i, j] = currmax
    z = np.empty_like(bin_img)
    for i in xrange(r):
        for j in xrange(c):
            left_idx = max(0, j-strt/2)
            right_idx = min(c, j+strt/2+1)
            currmax = y[i,left_idx]
            for jj in xrange(left_idx+1, right_idx):
                elt = y[i,jj]
                if elt > currmax:
                    currmax = elt
            z[i,j] = currmax
    return z

@jit
def erosion(bin_img, strt=3):
    r,c = bin_img.shape
    pad = int(strt)/2
    pad_shape = (r+pad*2,c+pad*2)
    strt_mask = np.ones((strt,strt),dtype=np.bool)
    input_pad_array = np.zeros(pad_shape,dtype=np.bool)
    input_pad_array[pad:r+pad,pad:c+pad] = bin_img
    binary_erosion = np.zeros(pad_shape,dtype=np.bool)
    for i in xrange(r):
        for j in xrange(c):
            binary_erosion[i+pad,j+pad] = np.min(input_pad_array[i:i+strt,j:j+strt])
    return binary_erosion[pad:r+pad,pad:c+pad]

def closing(bin_img):
	return dilation(erosion(bin_img))
