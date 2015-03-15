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
    y = np.empty_like(bin_img)
    for i in xrange(r):
        for j in xrange(c):
            left_idx = max(0, i-strt/2)
            right_idx = min(r, i+strt/2+1)
            currmin = bin_img[left_idx, j]
            for ii in xrange(left_idx+1, right_idx):
                elt = bin_img[ii, j]
                if elt < currmin:
                    currmin = elt
            y[i, j] = currmin
    z = np.empty_like(bin_img)
    for i in xrange(r):
        for j in xrange(c):
            left_idx = max(0, j-strt/2)
            right_idx = min(c, j+strt/2+1)
            currmin = y[i,left_idx]
            for jj in xrange(left_idx+1, right_idx):
                elt = y[i,jj]
                if elt < currmin:
                    currmin = elt
            z[i,j] = currmin
    return z

def closing(bin_img, strt=3):
	return dilation(erosion(bin_img,strt),strt)

def opening(bin_img, strt=3):
	return erosion(dilation(bin_img,strt),strt)
