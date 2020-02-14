# -*- coding: utf-8 -*-#
import RPi.GPIO as gpio

gpio.setmode(gpio.BOARD) #BOARD pin számozás használata, mindig változatlan
# gpio.setmode(gpio.BCM) #Broadcom pin számozás, hardverspecifikus, megváltozhat!
gpio.setwarnings(False)

# Stepper motorok gpio pinout - tomb formatumban tarolva
# Motor 0, 1 és 2 gpio portjai
motor_gpio = [26, 24, 22]
motor_dir = [40, 38, 36]
motor_enable = [0, 0, 0]
motor_grab = [0, 0, 0, 0]

# Gpio setupok - ciklussal
gpio_array = motor_gpio + motor_dir + motor_enable + motor_grab

for k in range(0,len(gpio_array)):
    if gpio_array[k] != 0: gpio.setup(gpio_array[k], gpio.OUT, initial=gpio.LOW)


def dir_set(mot, dir):
    """ Adott motor iránybeállítása (CW vagy CCW) """
    if dir == 1:
        gpio.output(motor_dir[mot], gpio.HIGH)
        print("Motor{0} forgásirány CW!".format(mot+1))
    elif dir == 0:
        gpio.output(motor_dir[mot], gpio.LOW)
        print("Motor{0} forgásirány CCW!".format(mot+1))
    else:
        print("Hibás iránybeállítás: Motor{0} - DIR:{1}!".format((mot+1), dir))


def enable_set(mot, enable):
    """ Adott motor engedélyezése vagy letiltása """
    if enable == 0:
        # gpio.output(motor_enable[mot], gpio.HIGH)
        print("Motor{0} letiltva!".format(mot+1))
    elif enable == 1:
        # gpio.output(motor_enable[mot-1], gpio.LOW)
        print("Motor{0} engedélyezve!".format(mot+1))
    else:
        print("Hibás engedélyezés: Motor{0} - ENABLE:{1}!".format((mot+1), enable))


def move(mot, level):
    """ Adott motor lépésjelének kiadása (fel vagy le) """
    if level == 1:
        gpio.output(motor_gpio[mot], gpio.HIGH)
        #print("Motor{0} kimenet magas!".format(mot+1))
    elif level == 0:
        gpio.output(motor_gpio[mot], gpio.LOW)
        #print("Motor{0} kimenet alacsony!".format(mot+1))
    else:
        print("Hibás lépésjel: Motor{0} - LEVEL:{1}!".format((mot+1), level))

def cleanup(): #GPIO pinout tisztítása
     gpio.cleanup()
