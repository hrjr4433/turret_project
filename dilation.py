#!/usr/bin/env python
# import the relevant libraries
import numpy as np
from scipy import ndimage
from parakeet import jit

@jit
def dilate_two_pass(x, k):
    m,n = x.shape
    y = np.empty_like(x).astype(bool)
    for i in xrange(m):
        for j in xrange(n):
            left_idx = max(0, i-k/2)
            right_idx = min(m, i+k/2+1)
            currmax = x[left_idx, j]
            for ii in xrange(left_idx+1, right_idx):
                elt = x[ii, j]
                if elt > currmax:
                    currmax = elt
            y[i, j] = currmax
    z = np.empty_like(x).astype(bool)
    for i in xrange(m):
        for j in xrange(n):
            left_idx = max(0, j-k/2)
            right_idx = min(n, j+k/2+1)
            currmax = y[i,left_idx]
            for jj in xrange(left_idx+1, right_idx):
                elt = y[i,jj]
                if elt > currmax:
                    currmax = elt
            z[i,j] = currmax
    return z 