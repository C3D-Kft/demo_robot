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
import spidev

# Stepper motorok (0, 1, ...) gpio pinoutjai - tömb formátumban tárolva
# Ha az érték nulla, akkor a program átugorja
motor_gpio = [26, 24, 22]
motor_dir = [40, 38, 36]
motor_enable = [37, 35, 33]
motor_grab = [0, 0, 0, 0]


def init():
    """ Raspberry Pi GPIO pinout inicializálása
    a fenti paraméterek alapján.
    """


    gpio.setmode(gpio.BOARD) # BOARD pin számozás, mindig változatlan
    # A gpio.BCM - Broadcom pin számozás hardverspecifikus ezért változhat!
    gpio.setwarnings(False)

    # GPIO pinek engedélyezése
    gpio_array = motor_gpio + motor_dir + motor_enable + motor_grab

    # Ha az érték nulla, akkor átugrom, mert nincs beállítva
    for k in range(0,len(gpio_array)):
        if gpio_array[k] != 0:
            gpio.setup(gpio_array[k], gpio.OUT, initial=gpio.LOW)

    # SPI Chip select beállítása
    gpio.setup(29, gpio.OUT, initial=gpio.HIGH)

    ### SPI ###
    # We only have SPI bus 0 available to us on the Pi
    bus = 0

    # Device is the chip select pin. Set to 0 or 1, depending on the connections
    device = 1

    # Enable SPI
    spi = spidev.SpiDev()

    # Open a connection to a specific bus and device (chip select pin)
    spi.open(bus, device)

    # Set SPI speed and mode
    spi.max_speed_hz = 5000
    spi.mode = 0b11 # CPOL=1, CPHA=1
    spi.lsbfirst = False

    msg = ""
    data = [[0x94557], [0xD001F], [0xE0010], [0x00008], [0xA8202]]

    # Set Chip select to High
    gpio.output(29, gpio.HIGH)

    for d in data:
        log.info("Data sent: {0}".format(d))
        # Data sending starts when chip select falls to LOW
        gpio.output(29, gpio.LOW)
        time.sleep(0.1)
        spi.xfer(d)
        time.sleep(0.1)
        # Data sending ends when chip select rises to HIGH
        gpio.output(29, gpio.HIGH)

        msg = spi.readbytes(3)
        log.info("Data received: {0}".format(msg))
        time.sleep(1)

    spi.close()
    time.sleep(2)


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
    """ Adott motor (0, 1, ...) engedélyezése (1) vagy letiltása (0). """

    msg = ""

    try:
        if enable == 0:
            gpio.output(motor_enable[mot], gpio.LOW)
            msg = "Motor{0} letiltva!".format(mot+1)
        elif enable == 1:
            gpio.output(motor_enable[mot], gpio.HIGH)
            msg = "Motor{0} engedélyezve!".format(mot+1)

    except:
        msg = ("Hibás engedélyezés: "
        + "Motor{0} - ENABLE:{1}!".format((mot+1), enable))

    finally:
        return msg


def step_mot(mot, level):
    """ Adott motor (0, 1, ...) lépésjelének kiadása (fel vagy le). """

    if level == 1:
        gpio.output(motor_gpio[mot], gpio.HIGH)
    elif level == 0:
        gpio.output(motor_gpio[mot], gpio.LOW)


def onestep_mot(mot, time_unit=0.1):
    """ Négszögjel generálása egy adott motor tengely számára. """

    gpio.output(motor_gpio[mot], gpio.HIGH)
    time.sleep(time_unit)
    gpio.output(motor_gpio[mot], gpio.LOW)
    time.sleep(time_unit)


def cleanup(): # GPIO pinout tisztítása
     gpio.cleanup()
