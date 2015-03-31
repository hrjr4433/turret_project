#!/usr/bin/env python

from parakeet import jit
import numpy as np

threshold = 0

# threshold
def otsu(gray):
    num_b = 256
    r,c = gray.shape
    total = r * c
    st = 0 # sum total
    hist = np.histogram(gray,num_b,[0,num_b])[0]
    for i in xrange(num_b):
        st += i*hist[i]
    wb = 0.0 # weight background
    sb = 0.0 # sum background
    thr_1 = 0.0
    thr_2 = 0.0
    mx = 0.0 # maximum
    for thr in xrange(num_b):
        wb += hist[thr]
        if wb == 0:
            continue
        wf = total - wb # weight foreground
        if wf == 0:
            break
        sb += thr * hist[thr]
        mb = sb / wb # mean background
        mf = (st - sb) / wf # mean foreground
        between = wb * wf * (mb - mf)**2
        if between >= mx:
            thr_1 = thr
            if between > mx:
                thr_2 = thr
            mx = between
    return int((thr_1+thr_2)/2)


def rgb_to_gray(rgb_img):
    return np.dot(rgb_img[...,:3], [.2126,.7152,.0722]).astype(np.uint8)

@jit
def gray_map(gray):
    return np.array([[[avg,avg,avg] for avg in col] for col in gray])

def thresholding(rgb_img):
    global threshold
    gray = rgb_to_gray(rgb_img)
    if threshold == 0:
        threshold = otsu(gray)
    return (gray < threshold)
