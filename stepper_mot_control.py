# -*- coding: utf-8 -*-#

""" Stepper motor control via GPIO for Raspberry Pi module. This module is
intended for controlling 3 stepper motor independently.

---- Info ----
C3D Kft. - Minden jog fenntartva a birtoklásra, felhasználásra,
sokszorosításra, szerkesztésre, értékesítésre nézve, valamint az ipari
tulajdonjog hatálya alá eső felhasználások esetén is.
www.C3D.hu
"""

import logging
import logger

log = logging.getLogger("Main")

import time
import RPi.GPIO as gpio


# Stepper motorok (0, 1, ...) gpio pinoutjai - tömb formátumban tárolva
# Ha az érték nulla, akkor a program átugorja
motor_gpio = [38, 10, 15] # 38, 10, 15
motor_dir = [40, 12, 13] # 35, 13, 38
motor_enable = [36, 8, 11] # 37, 11, 36
motor_grab = [37, 35, 33, 31] # 37, 35, 33, 31
spi_select = [18, 16]


def init():
    """ Raspberry Pi GPIO pinout inicializálása
    a fenti paraméterek alapján.
    """


    gpio.setmode(gpio.BOARD) # BOARD pin számozás, mindig változatlan
    # A gpio.BCM - Broadcom pin számozás hardverspecifikus ezért változhat!
    gpio.setwarnings(False)

    # GPIO pinek engedélyezése
    gpio_array = motor_gpio + motor_dir + motor_enable + motor_grab + spi_select

    # Ha az érték nulla, akkor átugrom, mert nincs beállítva
    for k in range(0,len(gpio_array)):
        if gpio_array[k] != 0:
            gpio.setup(gpio_array[k], gpio.OUT, initial=gpio.LOW)


def select_spi(mot):
    """ Adott motorhoz tartozó SPI választó kombinációk. """

    # spi_select = [18, 16]
    if mot == 1:
        gpio.output(spi_select[0], gpio.HIGH)
        gpio.output(spi_select[1], gpio.LOW)

    if mot == 2:
        gpio.output(spi_select[0], gpio.LOW)
        gpio.output(spi_select[1], gpio.HIGH)

    if mot == 3:
        gpio.output(spi_select[0], gpio.HIGH)
        gpio.output(spi_select[1], gpio.HIGH)


def dir_set(mot, dir):
    """ Adott motor (0, 1, ...) iránybeállítása (CW (1) vagy CCW (0)). """

    msg = ""

    try:
        if dir == 1:
            gpio.output(motor_dir[mot], gpio.HIGH)
            msg = "Motor{0} forgásirány CW!".format(mot+1)
        elif dir == 0:
            gpio.output(motor_dir[mot], gpio.LOW)
            msg = "Motor{0} forgásirány CCW!".format(mot+1)

    except:
        msg = ("Hibás iránybeállítás: "
        + "Motor{0} - DIR:{1}!".format((mot+1), dir))

    finally:
        return msg


def enable_set(mot, enable):
    """ Adott motor (0, 1, ...) engedélyezése (0) vagy letiltása (1). """

    msg = ""

    # Enable function has inverz logic - LOW: ENABLED, HIGH: DISABLED
    try:
        if enable == 0:
            gpio.output(motor_enable[mot], gpio.LOW)
            msg = "Motor{0} engedélyezve!".format(mot+1)
        elif enable == 1:
            gpio.output(motor_enable[mot], gpio.HIGH)
            msg = "Motor{0} letiltva!".format(mot+1)

    except:
        msg = ("Hibás engedélyezés: "
        + "Motor{0} - ENABLE:{1}!".format((mot+1), enable))

    finally:
        return msg


# def step_mot(mot, level):
#     """ Adott motor (0, 1, ...) lépésjelének kiadása (fel vagy le). """
#
#     if level == 1:
#         gpio.output(motor_gpio[mot], gpio.HIGH)
#     elif level == 0:
#         gpio.output(motor_gpio[mot], gpio.LOW)

def step_grabber():

    pass


def onestep_mot(mot, time_unit=0.1):
    """ Négszögjel generálása egy adott motor tengely számára. """

    gpio.output(motor_gpio[mot], gpio.HIGH)
    time.sleep(time_unit)
    gpio.output(motor_gpio[mot], gpio.LOW)
    time.sleep(time_unit)


def cleanup(): # GPIO pinout tisztítása
     gpio.cleanup()
