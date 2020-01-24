import RPi.GPIO as gpio
import time
import sys


gpio.setmode(gpio.BCM)
gpio.setwarnings(False)

#Stepper motorok gpio pinout - tomb formatumban tarolva
motor_gpio = [17, 0]
motor_dir = [0, 0]
motor_enable = [0, 0]
motor_grab = [0, 1, 2, 3]

#Gpio setupok
gpio.setup(motor_gpio[0], gpio.OUT)
gpio.setup(motor_gpio[1], gpio.OUT)
gpio.setup(motor_dir[0], gpio.OUT)
gpio.setup(motor_dir[1], gpio.OUT)
gpio.setup(motor_enable[0], gpio.OUT)
gpio.setup(motor_enable[1], gpio.OUT)
# gpio.setup(motor_grab[0], gpio.OUT)
# gpio.setup(motor_grab[1], gpio.OUT)
# gpio.setup(motor_grab[2], gpio.OUT)
# gpio.setup(motor_grab[3], gpio.OUT)


def dir_set(mot, dir): #Mot számú motor iránybeállítása
    if dir == 1:
        gpio.output(motor_dir[mot-1], gpio.HIGH)
    elif dir == 0:
        gpio.output(motor_dir[mot-1], gpio.LOW)
    else:
        print("Hibás iránybeállítás: Motor{0} - Dir:{1}".format(mot, dir))


def enable_set(mot, enable): #Mot számú motor engedélyezése
    if enable == 1:
        gpio.output(motor_enable[mot-1], gpio.HIGH)
    elif enable == 0:
        gpio.output(motor_enable[mot-1], gpio.LOW)
    else:
        print("Hibás engedélyezés: Motor{0} - Enable:{1}".format(mot, enable))


def move(mot, level): #Mot számú motor lépésjel kiadás (fel vagy le)
    if level == 1:
        gpio.output(motor_gpio[mot-1], gpio.HIGH)
    elif level == 0:
        gpio.output(motor_gpio[mot-1], gpio.LOW)


def cleanup():
    gpio.cleanup()
