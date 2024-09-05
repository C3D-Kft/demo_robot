# -*- coding: utf-8 -*-#

""" This file emulates the behavior of the Raspberry Pi GPIO module.

---- Info ----
C3D Kft. - Minden jog fenntartva a birtoklásra, felhasználásra,
sokszorosításra, szerkesztésre, értékesítésre nézve, valamint az ipari
tulajdonjog hatálya alá eső felhasználások esetén is.
www.C3D.hu
"""

# First import should be the logging module if any!
import logging

log = logging.getLogger("Main")

# NOTE: A valós értékek integer számok (!)
#  A print függvények egyszerűsége érdekében szöveggé lettek alakítva!
BOARD = "BOARD"
BCM = "BCM"
OUT = "OUT"
IN = "IN"
LOW = "LOW"
HIGH = "HIGH"

def setmode(a):
    log.info("{0} mode is used for GPIO numbering!".format(a))

def setup(a, b, initial=None):
    log.info("GPIO {0} set to: {1}, value: {2}".format(a,b, initial))

# NOTE: Function turned off, because spamming the console!
def output(a, b):
    pass
    log.info("GPIO {0} set to: {1}".format(a,b))

def cleanup():
    log.info("GPIO pins cleaned up!")

def setwarnings(flag):
    log.info("Warnings set to: {0}".format(flag))
