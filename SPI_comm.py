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
import struct
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
    # data_dec = [[607575], [851999], [917520], [4], [688642]]
    data_hex = [0x94557, 0xD001F, 0xE0010, 0x00004, 0xA8200]

    data = hex_to_bytes(data_hex)

    for d in data:
        tx = bytes_to_hex(d)
        log.info("TX: {0}".format(tx))
        recvd = spi.xfer(d) # Send transfer and listen for answer
        rx = bytes_to_hex(recvd)
        log.info("RX: {0}".format(rx))

        time.sleep(0.5)

    spi.close()


def hex_to_bytes(hex_list):
    """ Convert a list of hexadecimal numbers to a list '3-byte array'. """

    data = []

    for h in hex_list:
        # Convert hexa number to byte list / big-endian, 4-byte number
        b = list(struct.pack('>i',h))
        # Drop the first byte to make 3-byte list and add to data list
        data.append(b[1:])

    return data


def bytes_to_hex(bytes):
    """ Create a string of hexadecimal numbers from a byte array.  """

    if bytes == None:
        return None
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
