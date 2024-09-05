# -*- coding: utf-8 -*-#

""" This file emulates the behavior of the SpiDev module.

---- Info ----
C3D Kft. - Minden jog fenntartva a birtoklásra, felhasználásra,
sokszorosításra, szerkesztésre, értékesítésre nézve, valamint az ipari
tulajdonjog hatálya alá eső felhasználások esetén is.
www.C3D.hu
"""

# First import should be the logging module if any!
import logging

log = logging.getLogger("Main")

# A print függvények egyszerűsége érdekében szöveggé lettek alakítva!


class SpiDev:

    def init(self):
        print("Hello")

    def open(self, a, b):
        log.info("Open a connection to a specific bus ({0}) and device ({1}).".format(a, b))

    def xfer(self, d):
        log.info("Transfer message: >> {0} <<".format(d))

    def readbytes(self, a):
        log.info("Read {0} bytes from device.".format(a))

    def close(self):
        log.info("Close connection.")
