# -*- coding: utf-8 -*-#

""" SPI communication for motor driver setup.

---- Help ----
* https://www.sigmdel.ca/michel/ha/rpi/spi_on_pi_en.html

---- Info ----
C3D Kft. - Minden jog fenntartva a birtoklásra, felhasználásra,
sokszorosításra, szerkesztésre, értékesítésre nézve, valamint az ipari
tulajdonjog hatálya alá eső felhasználások esetén is.
www.C3D.hu
"""

import time
import spidev


def init():
    """ ... """

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
    spi.loop = False # This is read-only on RasPi
    spi.bits_per_word = 8 # This is read-only on RasPi
    # spi.cshigh = False
    # spi.no_cs = True
    spi.max_speed_hz = 4800
    spi.mode = 3 # 0b11 # CPOL=1, CPHA=1
    spi.lsbfirst = False

    # Random data
    msg = ""
    data_dec = [[607575], [851999], [917520], [8], [688642]]
    data_hex = [0x94557, 0xD001F, 0xE0010, 0x00008, 0xA8202]

    data = [[0x09, 0x45, 0x57],
    [0x0D, 0x00, 0x1F],
    [0x0E, 0x00, 0x10],
    [0x00, 0x00, 0x08],
    [0x0A, 0x82, 0x02]]


    def BytesToHex(Bytes):
        return ''.join(["0x%02X " % x for x in Bytes]).strip()


    for d in data:
        time.sleep(0.1)
        print("TX:", d)
        recvd = spi.xfer(d)
        print("RX:", recvd)

        # a = BytesToHex(recvd)
        # print(a)

        time.sleep(0.5)
        # msg = spi.readbytes(3)
        # print(msg)

    spi.close()


# Főprogram
if __name__ == "__main__":

    try:
        import logging
        import logger

        logger.init_logger()
        log = logging.getLogger("Main")
        log.info("Program started!")

        init()

    finally:
        print("Finished!")
