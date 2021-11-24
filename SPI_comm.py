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

import logging
log = logging.getLogger("Main")

import time
import spidev



def init():
    """ Initializes motor drivers by sending the setup
    bytes to them via SPI communication.
    """

    # Enable SPI
    spi = spidev.SpiDev()

    # Open a connection to a specific bus and device (chip select pin)
    # We only have SPI bus 0 available to us on the Pi
    # Device is the chip select pin. Set to 0 or 1, depending on the connections
    bus = 0
    device = 1
    spi.open(bus, device)

    # Set SPI configs
    spi.loop = False # This is read-only on RasPi
    spi.bits_per_word = 8 # This is read-only on RasPi
    spi.max_speed_hz = 4800
    spi.mode = 3 # 0b11 # CPOL=1, CPHA=1
    spi.lsbfirst = False

    # Driver setup data
    msg = ""
    data_dec = [[607575], [851999], [917520], [8], [688642]]
    data_hex = [0x94557, 0xD001F, 0xE0010, 0x00008, 0xA8202]

    data = [[0x09, 0x45, 0x57],
    [0x0D, 0x00, 0x1F],
    [0x0E, 0x00, 0x10],
    [0x00, 0x00, 0x08],
    [0x0A, 0x82, 0x02]]

    for d in data:
        log.info("TX: {0}".format(d))
        recvd = spi.xfer(d)
        log.info("RX: {0}".format(recvd))

        # log.info(bytes_to_hex(recvd))

        time.sleep(0.5)
        # msg = spi.readbytes(3)
        # print(msg)

    spi.close()


def hex_to_bytes(hex):
    pass


def bytes_to_hex(bytes):

    if bytes == None:
        return
    else:
        return ''.join(["0x%02X " % x for x in bytes]).strip()


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
