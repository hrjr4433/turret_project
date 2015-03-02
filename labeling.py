#!/usr/bin/env python

# rgb detection
import numpy as np
from parakeet import jit


@jit
def labeling(bin_img):
    r,c = bin_img.shape
    int_img = np.zeros((r,c),dtype=np.uint8)
    label = 1
    for i in xrange(r):
        for j in xrange(c):
            if bin_img[i,j]:
                if bin_img[i-1,j]:
                    int_img[i,j] = int_img[i-1,j]
                elif bin_img[i,j-1]:
                    int_img[i,j] = int_img[i,j-1]
                else:
                    int_img[i,j] = label
                    label += 1
    return int_img

def label_items(bin_img, min=30):
    int_img = labeling(bin_img)
    num_items = np.max(int_img)
    for i in range(1,num_items+1):
        mask = (int_img == i)
        if mask.sum() < min:
            int_img[mask] = 0
    return int_img
