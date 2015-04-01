#!/usr/bin/python

from Adafruit_PWM_Servo_Driver import PWM

# Initialise the PWM device using the default address
pwm = PWM(0x40)
# Note if you'd like more debug output you can instead run:
#pwm = PWM(0x40, debug=True)

servoMin = 340  #140  # Min pulse length out of 4096
servoMid = 400  # mid point
servoMax = 460  #660  # Max pulse length out of 4096
servoTrg = 450  # triger point
servo_x = 0 # servo x channel
servo_y = 1 # servo y channel
servo_t = 2 # servo trigger channel

def setServoPulse(channel, pulse):
    pulseLength = 1000000                   # 1,000,000 us per second
    pulseLength /= 60                       # 60 Hz
    print "%d us per period" % pulseLength
    pulseLength /= 4096                     # 12 bits of resolution
    print "%d us per bit" % pulseLenth
    pulse *= 1000
    pulse /= pulseLength
    pwm.setPWM(channel, 0, pulse)

# def __init__(self):
# pwm = PWM(0x40)

def get_pulses(degrees):
    y,x = degrees
    pulse_per_degree = (servoMax-servoMin)/float(60)
    return (servoMid+int(y*pulse_per_degree), servoMid+int(x*pulse_per_degree))

def ready():
    pwm.setPWM(servo_x, 0, servoMid)
    pwm.setPWM(servo_y, 0, servoMid)
    pwm.setPWM(servo_t, 0, servoMid)

def move_by_degrees(degrees):
    y,x = get_pulses(degrees)
    pwm.setPWM(servo_x, 0, x)
    pwm.setPWM(servo_y, 0, y-25) # camera position is lower than weapon

def fire():
    pwm.setPWM(servo_t, 0, servoTrg)

