#!/usr/bin/env python3
# flake8: noqa
########################################################################
# Filename    : UltrasonicRanging.py
# Description : Get distance via UltrasonicRanging sensor
# auther      : www.freenove.com
# modification: 2019/12/28
########################################################################
import time

import RPi


trigPin = 16
echoPin = 18
MAX_DISTANCE = 220  # define the maximum measuring distance, unit: cm
timeOut = (
    MAX_DISTANCE * 60
)  # calculate timeout according to the maximum measuring distance


def pulseIn(pin, level, timeOut):  # obtain pulse time of a pin under timeOut
    t0 = time.time()
    while RPi.GPIO.input(pin) != level:
        if (time.time() - t0) > timeOut * 0.000001:
            return 0
    t0 = time.time()
    while RPi.GPIO.input(pin) == level:
        if (time.time() - t0) > timeOut * 0.000001:
            return 0
    pulseTime = (time.time() - t0) * 1000000
    return pulseTime


def getSonar():  # get the measurement results of ultrasonic module,with unit: cm
    RPi.GPIO.output(trigPin, RPi.GPIO.HIGH)  # make trigPin output 10us HIGH level
    time.sleep(0.1)  # 10us
    RPi.GPIO.output(trigPin, RPi.GPIO.LOW)  # make trigPin output LOW level
    pingTime = pulseIn(echoPin, RPi.GPIO.HIGH, timeOut)  # read plus time of echoPin
    distance = (
        pingTime * 340.0 / 2.0 / 10000.0
    )  # calculate distance with sound speed 340m/s
    distance


def setup():
    RPi.GPIO.setmode(RPi.GPIO.BOARD)  # use PHYSICAL RPi.GPIO Numbering
    RPi.GPIO.setup(trigPin, RPi.GPIO.OUT)  # set trigPin to OUTPUT mode
    RPi.GPIO.setup(echoPin, RPi.GPIO.IN)  # set echoPin to INPUT mode


def looop():
    while True:
        distance = getSonar()  # get distance
        print("Distance: %.2f cm" % (distance))
        time.sleep(0.01)


if __name__ == "__main__":  # Program entrance
    print("Program is starting...")
    setup()
    try:
        looop()
    except KeyboardInterrupt:  # Press ctrl-c to end the program.
        RPi.GPIO.cleanup()  # release RPi.GPIO resource
