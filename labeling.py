#!/usr/bin/env python

# rgb detection
import numpy as np
from parakeet import jit

@jit
def labeling(bin_img):
    # first pass
    r,c = bin_img.shape
    int_img = np.zeros((r,c),dtype=np.uint8)
    label = 0
    for i in xrange(r):
        for j in xrange(c):
            if bin_img[i,j]:
                min_r = max(0,i-1)
                max_r = max(r,i+1)
                min_c = max(0,j-1)
                max_c = min(c,j+2)
                min_label = 0
                for ii in xrange(min_r,max_r):
                    for jj in xrange(min_c,max_c):
                        if bin_img[ii,jj] and int_img[ii,jj]:
                            if not min_label or (min_label and int_img[ii,jj] < min_label):
                                min_label = int_img[ii,jj]
                if min_label:
                    int_img[i,j] = min_label
                else:
                    int_img[i,j] = label
                    label += 1
    for i in xrange(r):
        for j in xrange(c):
            if bin_img[i,j]:
                max_r = max(r,i+5)
                max_c = min(c,j+5)
                min_label = 0
                for ii in xrange(i,max_r):
                    for jj in xrange(j,max_c):
                        if int_img[ii,jj]:
                            if not min_label or (min_label and int_img[ii,jj] < min_label):
                                min_label = int_img[ii,jj]
                int_img[i,j] = min_label
    return int_img

def find_biggest_object(bin_img):
    int_img = labeling(bin_img)
    num_obj = np.max(int_img)
    biggest = np.zeros(bin_img.shape, dtype=np.bool)
    biggest_num_pix = 0
    for i in range(1,num_obj+1):
        mask = (int_img == i)
        mask_sum = mask.sum()
        if  mask_sum > biggest_num_pix:
            biggest_num_pix = mask_sum
            biggest = np.array(mask)
    return biggest
