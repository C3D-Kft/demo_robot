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
import queue

log = logging.getLogger("Main")

# robot_control_gui - gomb hozzáadása - kapcsolat létrehozása / rögzítés elkezdése
# gomb hozzáadása - rögzítése megállítása, fájl létrehozása


def initialize():
    ser = serial.Serial('/dev/ttyACM0', 9600)
    s = [0]
    while True:
        read_serial = ser.readline()
        s[0] = str(int(ser.readline(), 16))
        print(s[0])
        print(read_serial)

def start_collect():
    pass

def stop_collect():
    pass

