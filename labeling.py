#!/usr/bin/env python

# labeling
import numpy as np
from parakeet import jit

@jit
def labeling(bin_img):
    # first loop
    r,c = bin_img.shape
    int_img = np.zeros((r,c),dtype=np.uint16)
    label = 0
    for i in xrange(r):
        for j in xrange(c):
            if bin_img[i,j]:
                min_r = max(0,i-1)
                max_r = min(r,i+2)
                min_c = max(0,j-1)
                max_c = min(c,j+2)
                min_label = label
                for ii in xrange(min_r,max_r):
                    for jj in xrange(min_c,max_c):
                        if bin_img[ii,jj] and int_img[ii,jj] > 0 and int_img[ii,jj] < min_label:
                                min_label = int_img[ii,jj]
                int_img[i,j] = min_label
                if min_label == label:
                    label += 1

    # second loop
    min_neighbor = np.zeros(label,dtype=np.uint16)
    for k in xrange(label):
        min_neighbor[k] = k
    for i in xrange(r):
        for j in xrange(c):
            if bin_img[i,j]:
                min_r = max(0,i-1)
                max_r = min(r,i+2)
                min_c = max(0,j-1)
                max_c = min(c,j+2)
                curr_label = int_img[i,j]
                min_label = curr_label
                for ii in xrange(min_r,max_r):
                    for jj in xrange(min_c,max_c):
                        if int_img[ii,jj] > 0 and int_img[ii,jj] < min_label:
                            min_label = int_img[ii,jj]
                if min_neighbor[curr_label] > min_label:
                    min_neighbor[curr_label] = min_label

    # third loop
    for k in xrange(label):
        l = k
        while min_neighbor[l] != l:
            l = min_neighbor[l]
        min_neighbor[k] = l
    for i in xrange(r):
        for j in xrange(c):
            if bin_img[i,j]:
                curr_label = int_img[i,j]
                if curr_label > min_neighbor[curr_label]:
                    int_img[i,j] = min_neighbor[curr_label]
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
