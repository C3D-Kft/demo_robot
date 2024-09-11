# -*- coding: utf-8 -*-#

""" xxx.

---- Info ----
C3D Kft. - Minden jog fenntartva a birtoklásra, felhasználásra,
sokszorosításra, szerkesztésre, értékesítésre nézve, valamint az ipari
tulajdonjog hatálya alá eső felhasználások esetén is.
www.C3D.hu
"""

# First import should be the logging module if any!
import logging
import serial

log = logging.getLogger("Main")


def main():
    ser = serial.Serial('/dev/ttyACM0', 9600)
    s = [0]
    while True:
        read_serial = ser.readline()
        s[0] = str(int(ser.readline(), 16))
        print(s[0])
        print(read_serial)
