import io
import pygame
from pygame import surfarray
from pygame.locals import *
import picamera
import picamera.array
import time
import threading
import numpy as np

done = False
lock = threading.Lock()
pool = []

pygame.init()
surfarray.use_arraytype('numpy')
size = (240,180)
screen = pygame.display.set_mode(size, 0)
camera = picamera.PiCamera()

class ImageProcessor(threading.Thread):
    def __init__(self):
        super(ImageProcessor, self).__init__()
        self.stream = picamera.array.PiRGBArray(camera)
        self.event = threading.Event()
        self.terminated = False
        self.setDaemon(True)
        self.start()

    def run(self):
        global done
        while not self.terminated:
            if self.event.wait(1):
                try:
                    self.stream.seek(0)
                    image = self.stream.array
                    mapped = surfarray.map_array(screen,image).transpose()
                    surfarray.blit_array(screen, mapped)
                    pygame.display.update() 
                    if pygame.event.poll() == pygame.QUIT:
                        pygame.quit()
                        done = True
                finally:
                    self.stream.seek(0)
                    self.stream.truncate()
                    self.event.clear()
                    with lock:
                        pool.append(self)

def streams():
    while not done:
        with lock:
            if pool:
                processor = pool.pop()
            else:
                processor = None
        if processor:
            yield processor.stream
            processor.event.set()
        else:
            time.sleep(0.1)

if camera != None:
    pool = [ImageProcessor() for i in range(4)]
    camera.resolution = size
    camera.framerate = 15
    camera.vflip = True
    time.sleep(2)
    camera.capture_sequence(streams(),'rgb', use_video_port=True)

while pool:
    with lock:
        processor = pool.pop()
    processor.terminated = True
    processor.join()

finally:
    camera.close()
    print ('Program Terminated')
