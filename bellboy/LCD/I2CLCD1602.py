#!/usr/bin/env python3
# flake8: noqa

"""
########################################################################
# Filename    : I2CLCD1602.py
# Description : Use the LCD display data
# Author      : freenove
# modification: 2018/08/03
########################################################################
"""

from datetime import datetime
from time import sleep, strftime

import RPi.GPIO as GPIO
from Adafruit_LCD1602 import Adafruit_CharLCD
from PCF8574 import PCF8574_GPIO
from UltrasonicRanging import getSonar


trigPin = 16
echoPin = 18
MAX_DISTANCE = 220  # define the maximum measuring distance, unit: cm
timeOut = (
    MAX_DISTANCE * 60
)  # calculate timeout according to the maximum measuring distance

# def get_cpu_temp():     # get CPU temperature and store it into file "/sys/class/thermal/thermal_zone0/temp"
#    tmp = open('/sys/class/thermal/thermal_zone0/temp')
#    cpu = tmp.read()
#    tmp.close()
#    return '{:.2f}'.format( float(cpu)/1000 ) + ' C'

# def get_time_now():     # get system time
#    return datetime.now().strftime('    %H:%M:%S')


def setup():
    GPIO.setmode(GPIO.BOARD)  # use PHYSICAL GPIO Numbering
    GPIO.setup(trigPin, GPIO.OUT)  # set trigPin to OUTPUT mode
    GPIO.setup(echoPin, GPIO.IN)  # set echoPin to INPUT mode


def loop():
    setup()
    mcp.output(3, 1)  # turn on LCD backlight
    lcd.begin(16, 2)  # set number of LCD lines and columns
    while True:
        # lcd.clear()
        lcd.setCursor(0, 0)  # set cursor position
        lcd.message("Hello Bellboy" + "\n")
        lcd.message("Distance:" + str(getSonar()))
        # lcd.message( 'CPU: ' + get_cpu_temp()+'\n' )# display CPU temperature
        # lcd.message( get_time_now() )   # display the time
        sleep(1)


def destroy():
    lcd.clear()


PCF8574_address = 0x27  # I2C address of the PCF8574 chip.
PCF8574A_address = 0x3F  # I2C address of the PCF8574A chip.
# Create PCF8574 GPIO adapter.
try:
    mcp = PCF8574_GPIO(PCF8574_address)
except:
    try:
        mcp = PCF8574_GPIO(PCF8574A_address)
    except:
        print("I2C Address Error !")
        exit(1)
# Create LCD, passing in MCP GPIO adapter.
lcd = Adafruit_CharLCD(pin_rs=0, pin_e=2, pins_db=[4, 5, 6, 7], GPIO=mcp)

if __name__ == "__main__":
    print("Program is starting ... ")
    try:
        loop()
    except KeyboardInterrupt:
        destroy()
        GPIO.cleanup()
