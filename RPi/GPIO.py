# -*- coding: utf-8 -*-#

""" This file emulates the behavior of the Raspberry Pi GPIO module.

---- Info ----
C3D Kft. - Minden jog fenntartva a birtoklásra, felhasználásra,
sokszorosításra, szerkesztésre, értékesítésre nézve, valamint az ipari
tulajdonjog hatálya alá eső felhasználások esetén is.
www.C3D.hu
"""

# A valós értékek integer számok (!)
# A print függvények egyszerűsége érdekében szöveggé lettek alakítva!
BOARD = "BOARD"
BCM = "BCM"
OUT = "OUT"
IN = "IN"
LOW = "LOW"
HIGH = "HIGH"

def setmode(a):
    print("{0} mode is used for GPIO numbering!".format(a))

def setup(a, b, initial=None):
    print("GPIO {0} set to: {1}, value: {2}".format(a,b, initial))

def output(a, b):
    pass
    # Function turned off, beacuse spamming the console!
    # print("GPIO {0} set to: {1}".format(a,b))

def cleanup():
    print("GPIO pins cleaned up!")

def setwarnings(flag):
    print("Warnings set to: {0}".format(flag))
