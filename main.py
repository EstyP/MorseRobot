#!/usr/bin/env python3

# Import the necessary libraries
import time
import math
from ev3dev2.motor import *
from ev3dev2.sound import Sound
from ev3dev2.sensor import *
from ev3dev2.sensor.lego import *
from ev3dev2.sensor.virtual import *

# Create the sensors and motors objects
motorA = LargeMotor(OUTPUT_A)
motorB = LargeMotor(OUTPUT_B)
left_motor = motorA
right_motor = motorB
tank_drive = MoveTank(OUTPUT_A, OUTPUT_B)
steering_drive = MoveSteering(OUTPUT_A, OUTPUT_B)

spkr = Sound()
radio = Radio()

color_sensor_in1 = ColorSensor(INPUT_1)
color_sensor_in2 = ColorSensor(INPUT_2)
ultrasonic_sensor_in3 = UltrasonicSensor(INPUT_3)
gyro_sensor_in4 = GyroSensor(INPUT_4)
gps_sensor_in5 = GPSSensor(INPUT_5)

motorC = LargeMotor(OUTPUT_C)  # Magnet

# Here is where your code starts

morse_eng_dict = {
    ".*-": "A",
    "-*.*.*.": "B",
    "-*.*-*.": "C",
    "-*.*.": "D",
    ".": "E",
    ".*.*-*.": "F",
    "-*-*.": "G",
    ".*.*.*.": "H",
    ".*.": "I",
    ".*-*-*-": "J",
    "-*.*-": "K",
    ".*-*.*.": "L",
    "-*-": "M",
    "-*.": "N",
    "-*-*-": "O",
    ".*-*-*.": "P",
    "-*-*.*-": "Q",
    ".*-*.": "R",
    ".*.*.": "S",
    "-": "T",
    ".*.*-": "U",
    ".*.*.*-": "V",
    ".*-*-": "W",
    "-*.*.*-": "X",
    "-*.*-*-": "Y",
    "-*-*.*.": "Z",
    "-*-*-*-*-": "0",
    ".*-*-*-*-": "1",
    ".*.*-*-*-": "2",
    ".*.*.*-*-": "3",
    ".*.*.*.*-": "4",
    ".*.*.*.*.": "5",
    "-*.*.*.*.": "6",
    "-*-*.*.*.": "7",
    "-*-*-*.*.": "8",
    "-*-*-*-*.": "9"
}

# PID algorithm variables
midpoint = None
integral = None
lasterror = None
startPosition = None
current = None
error = None
PID = None
dotMeasurement = None
measurementOne = None
measurementTwo = None
lasterror = error

# PID variable assignment
midpoint = 50
integral = 0
lasterror = 0

# First dot measurement variables
dotMeasurement = 0
measurementOne = 0
measurementTwo = 0
lastColour = 0

# General measuring variables
measurementThree = 0
measurementFour = 0
measurementTaken = 0
multiple = 0

# morse search variables

res = 0
morseString = ''
morseList = 0


# functions

def CorrectSteering():  # Applies the PID tuning algorithm to correct steering
    global midpoint
    global integral
    global lasterror
    current = color_sensor_in2.reflected_light_intensity
    error = current - midpoint
    integral = error + integral * 0.5
    PID = (0.07 * error + 0.03 * integral) + 1 * (error - lasterror)
    steering_drive.on(PID, 20)


def MeasureFirstDot():  # checks for the first dot and measures it
    global measurementOne
    global measurementTwo
    global dotMeasurement
    if colour == 5 and dotMeasurement == 0:
        measurementOne = motorA.position
    if colour != 5 and dotMeasurement == 0 and measurementOne != 0:
        measurementTwo = motorA.position
        dotMeasurement = measurementTwo - measurementOne


def MeasureBars(colour):  # Measures the bars within which the message is encoded
    global measurementThree, measurementFour, dotMeasurement, multiple

    # if first dot not taken, take it
    if dotMeasurement == 0:
        MeasureFirstDot()
    # first dot already taken, measure subsuquent bars
    else:
        if colour == 5:
            measurementThree = motorA.position
            multiple = (measurementThree - measurementFour) / dotMeasurement
        else:
            measurementFour = motorA.position
            multiple = (measurementFour - measurementThree) / dotMeasurement


def AssignValues(colour):  # assign values to the multiples
    global multiple, morseString

    if colour == 5:
        if 0 < multiple <= 1.5:
            morseString += "*"
        elif 1.5 < multiple <= 5:
            search_key = morseString
            res = [val for key, val in morse_eng_dict.items() if search_key == key]
            print(res)
            morseString = ""
        elif multiple > 5:
            search_key = morseString
            res = [val for key, val in morse_eng_dict.items() if search_key == key]
            print(res)
            print("")
            morseString = ""
    if colour != 5:
        if 0 < multiple <= 1.8:
            morseString += "."
        elif multiple > 1.8:
            morseString += "-"


# Start the robot moving
while not color_sensor_in2.reflected_light_intensity < 100:
    tank_drive.on(20, 20)

# Main reaction loop
while True:
    # Set the current colour to detect any changes
    colour = color_sensor_in1.color

    # PID Steering algorithm
    CorrectSteering()

    # has the colour changed
    if colour != lastColour:
        lastColour = colour  # update the colour

        MeasureBars(colour)

        AssignValues(colour)

