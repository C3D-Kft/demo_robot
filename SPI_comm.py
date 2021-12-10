# -*- coding: utf-8 -*-#

""" SPI communication for motor driver setup.

---- Help ----
* https://www.sigmdel.ca/michel/ha/rpi/spi_on_pi_en.html
* https://stackoverflow.com/questions/15036551/best-way-to-split-a-hexadecimal
* https://docs.python.org/3.5/library/struct.html
* https://stackoverflow.com/questions/32675679/convert-binary-string-to-bytearray-in-python-3

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


class SPI():


    def init(self):
        """ Initializes motor drivers by sending the setup
        bytes to them via SPI communication.
        """

        # Enable SPI
        self.spi = spidev.SpiDev()

        # Open a connection to a specific bus and device (chip select pin)
        # We only have SPI bus 0 available to us on the Pi
        # Device is the chip select pin. Set to 0 or 1, depending on the connections
        bus = 0
        device = 1
        self.spi.open(bus, device)

        # Set SPI configs
        self.spi.loop = False # This is read-only on RasPi
        self.spi.bits_per_word = 8 # This is read-only on RasPi
        self.spi.max_speed_hz = 20000
        self.spi.mode = 3 # 0b11 # CPOL=1, CPHA=1
        self.spi.lsbfirst = False


    def start(self):

        # Driver setup data
        msg = ""

        DRVCTRL = "0000 0000 0000 0000 0001" # 00001
        CHOPCONF = "1001 0100 0101 0101 0111" # 94557
        SMARTEN = "1010 1000 0010 0000 0010" # A8202
        SGCSCONF = "1101 0000 0000 0001 1111" # D001F
        DRVCONF = "1110 0000 0000 0010 0000" # E0020

        # Convert bitstrings to integer
        bs_list = [CHOPCONF, SGCSCONF, DRVCONF, DRVCTRL, SMARTEN]

        data_int = []

        for bs in bs_list:
            bs = ''.join(bs.split())
            data_int.append(int(bs,2))

        # Convert integer list to bytearray
        data = int_to_bytes(data_int)

        for d in data:
            tx = bytearray_to_bitstring(d)
            log.info("TX: {0}".format(tx))
            recvd = self.spi.xfer(d) # Send transfer and listen for answer
            rx = bytearray_to_bitstring(recvd)
            log.info("RX: {0}".format(rx))
            time.sleep(0.5)


    def readback(self):

        READBACK = "0100 0000 0000 0000 0000" # 00001

        rbck = ''.join(READBACK.split())
        rbck = int(rbck,2)
        data = int_to_bytes([rbck])

        rb = self.spi.xfer(data[0]) # Send transfer and listen for answer
        rb = bytearray_to_bitstring(rb)
        log.info("RBCK: {0}".format(rb))
        log_readback(rb)


    def close(self):
        self.spi.close()


def bytearray_to_bitstring(bytearray):

    if bytearray == None:
        return None

    s = ""
    for b in bytearray:
        s += "{:08b}-".format(b)

    return s[4:-1]


def log_readback(bitstring):

    bitstring = bitstring.replace("-","")
    bitstring = bitstring.strip()

    if bitstring[19] == "1": # SG
        log.warning("StallGuard2 threshold has been reached!")

    if bitstring[18] == "1": # OT
        log.critical("Overtemperature shutdown!")

    if bitstring[17] == "1": # OTPW
        log.warning("Overtemperature warning!")

    if (bitstring[16] == "1") or (bitstring[15] == "1"): # S2GA / S2GB
        log.critical("Short to GND condition on high-side transistors!")

    if (bitstring[14] == "1") or (bitstring[13] == "1"): # OLA / OLB
        log.info("Open load condition!")

    if bitstring[12] == "1": # STST
        log.warning("Standstill condition!")


def int_to_bytes(int_list):
    """ Convert a list of integers to a list '3-byte array'. """

    data = []

    for h in int_list:
        d = []
        # Convert hexa number to byte list / big-endian, 4-byte int
        b = list(struct.pack('>i',h))
        # Drop the first byte to make 3-byte list and add to data list
        for bi in b[1:]: d.append(int(bi))
        data.append(d)

    return data


# def bytes_to_hex(bytes):
#     """ Create a string of hexadecimal numbers from a byte array. """
#
#     if bytes == None:
#         return None
#     else:
#         return ''.join(["0x%02X " % x for x in bytes]).strip()


# Főprogram
if __name__ == "__main__":

    try:
        import logging
        import logger

        logger.init_logger()
        log = logging.getLogger("Main")
        log.info("Program started!")

        # init()

    finally:
        print("Finished!")
