# -*- coding: utf-8 -*-#

""" Stepper motor control via GPIO for Raspberry Pi module. This module is
intended for controlling 3 stepper motor independently.

---- Info ----
C3D Kft. - Minden jog fenntartva a birtoklásra, felhasználásra,
sokszorosításra, szerkesztésre, értékesítésre nézve, valamint az ipari
tulajdonjog hatálya alá eső felhasználások esetén is.
www.C3D.hu
"""


import time
import RPi.GPIO as gpio


# Stepper motorok (0, 1, 2) gpio pinoutjai - tömb formátumban tárolva
# Ha az érték nulla, akkor a program átugorja
## BOARD
motor_step = [38, 29, 11]
motor_dir = [36, 7, 13]
motor_enable = [40, 32, 15]
motor_grip = [37, 35, 33, 31]
spi_select = [18, 16]
POWER = [3]

##BCM
# motor_step = [20, 5, 17]
# motor_dir = [16, 0, 27]
# motor_enable = [21, 12, 22]
# motor_grip = [26, 19, 13, 6]
# spi_select = [24, 23]
# power = [2]

GRIPPER_STATUS = 0


def init():
    """ Raspberry Pi GPIO pinout inicializálása
    a fenti paraméterek alapján.
    """

    gpio.setmode(gpio.BOARD) # BOARD pin számozás, mindig változatlan
    # gpio.setmode(gpio.BCM) # Broadcom pin számozás hardverspecifikus ezért változhat!
    gpio.setwarnings(False)

    # GPIO pinek engedélyezése
    gpio_array = motor_step + motor_dir + motor_enable + motor_grip + spi_select + POWER

    # Ha az érték nulla, akkor átugrom, mert nincs beállítva
    for k in gpio_array:
        if k != 0:
            gpio.setup(k, gpio.OUT, initial=gpio.LOW)


def select_spi(mot):
    """ Adott motorhoz tartozó SPI választó kombinációk. """

    if mot == 1:
        gpio.output(spi_select[0], gpio.HIGH)
        gpio.output(spi_select[1], gpio.LOW)

    if mot == 2:
        gpio.output(spi_select[0], gpio.LOW)
        gpio.output(spi_select[1], gpio.HIGH)

    if mot == 3:
        gpio.output(spi_select[0], gpio.HIGH)
        gpio.output(spi_select[1], gpio.HIGH)


def dir_set(mot, direction):
    """ Adott motor (0, 1, ...) iránybeállítása (CW (1) vagy CCW (0)). """

    msg = ""

    try:
        if direction == 1:
            gpio.output(motor_dir[mot], gpio.HIGH)
            msg = f"Motor{mot+1} forgásirány CW!"
        elif direction == 0:
            gpio.output(motor_dir[mot], gpio.LOW)
            msg = f"Motor{mot+1} forgásirány CCW!"

    except:
        msg = f"Hibás iránybeállítás: Motor{mot+1} - DIR:{direction}!"

    finally:
        return msg


def enable_set(mot, enable):
    """ Adott motor (0, 1, ...) engedélyezése (0) vagy letiltása (1). """

    msg = ""

    # Enable function has inverz logic - LOW: ENABLED, HIGH: DISABLED
    try:
        if enable == 0:
            gpio.output(motor_enable[mot], gpio.LOW)
            msg = f"Motor{mot+1} engedélyezve!"
        elif enable == 1:
            gpio.output(motor_enable[mot], gpio.HIGH)
            msg = f"Motor{mot+1} letiltva!"

    except:
        msg = f"Hibás engedélyezés: Motor{mot+1} - ENABLE:{enable}!"

    finally:
        return msg


def step_gripper(direction):
    """ Gripper motor léptetése az iránybeállításnak megfelelően
    (CW (1) vagy CCW (0)).
    """

    global GRIPPER_STATUS

    step_table = [
    [gpio.LOW, gpio.LOW, gpio.LOW, gpio.HIGH], #4
    [gpio.LOW, gpio.LOW, gpio.HIGH, gpio.HIGH], #4-3
    [gpio.LOW, gpio.LOW, gpio.HIGH, gpio.LOW], #3
    [gpio.LOW, gpio.HIGH, gpio.HIGH, gpio.LOW], #3-2
    [gpio.LOW, gpio.HIGH, gpio.LOW, gpio.LOW], #2
    [gpio.HIGH, gpio.HIGH, gpio.LOW, gpio.LOW], #1-2
    [gpio.HIGH, gpio.LOW, gpio.LOW, gpio.LOW], #1
    [gpio.HIGH, gpio.LOW, gpio.LOW, gpio.HIGH] #1-4
    ]

    print("Move starts!")

    for i in range(0,512):

        if direction == 1:
            GRIPPER_STATUS += 1
            if GRIPPER_STATUS == 8: # If out-of-range upwards
                GRIPPER_STATUS = 0

        elif direction == 0:
            GRIPPER_STATUS -= 1
            if GRIPPER_STATUS == -1: # If out-of-range downwards
                GRIPPER_STATUS = 7

        # Set the coil pin output according to the actual step table
        # print("Gripper status: {}".format(GRIPPER_STATUS))
        for k in range(4):
            gpio.output(motor_grip[k], step_table[GRIPPER_STATUS][k])

        time.sleep(0.001)

    print("Move ready!")
    for k in range(4):
        gpio.output(motor_grip[k], gpio.LOW)


def onestep_mot(mot, time_unit=0.1):
    """ Négszögjel generálása egy adott motor tengely számára. """

    gpio.output(motor_step[mot], gpio.HIGH)
    time.sleep(time_unit)
    gpio.output(motor_step[mot], gpio.LOW)
    time.sleep(time_unit)


def poweron():
    """ 24V tápfeszültség bekapcsolása. """

    gpio.output(POWER[0], gpio.HIGH)


def poweroff():
    """ 24V tápfeszültség kikapcsolása. """

    gpio.output(POWER[0], gpio.LOW)


def cleanup(): # GPIO pinout tisztítása
    gpio.cleanup()
