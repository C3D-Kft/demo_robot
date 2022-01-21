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
import stepper_mot_control as smc



class SPI():


    def init(self):
        """ Initializes motor drivers by sending the setup
        bytes to them via SPI communication.
        """

        self.MOTOR = 0 # Choosen motor number (1-3, default zero)

        # Enable SPI
        self.spi = spidev.SpiDev()

        # Open a connection to a specific bus and device (chip select pin)
        # We only have SPI bus 0 available on the RPi
        # Device is the chip select pin. Set to 0 or 1, depending on the RPi connections
        # The chip select pin is also connected to a multiplexer on the PCB,
        # so selector pins are needed to choose which motor driver to use
        bus = 0
        device = 1
        self.spi.open(bus, device)

        # Set SPI configs
        self.spi.loop = False # This is read-only on RasPi
        self.spi.bits_per_word = 8 # This is read-only on RasPi
        self.spi.max_speed_hz = 20000
        self.spi.mode = 3 # 0b11 # CPOL=1, CPHA=1
        self.spi.lsbfirst = False

        for i in [1,2,3]:
            self.spi_select(i)
            self.start(i)


    def start(self):
        """ Send motor driver configuration data
        to the selected motor driver.
        """

        msg = ""

        DRVCTRL = "0000 0000 0000 0000 0001" # 00001
        CHOPCONF = "1001 0100 0101 0101 0111" # 94557
        SMARTEN = "1010 1000 0010 0000 0010" # A8202
        SGCSCONF = "1101 0000 0000 0001 1111" # D001F
        DRVCONF = "1110 0000 0000 0010 0000" # E0020

        bs_list = [CHOPCONF, SGCSCONF, DRVCONF, DRVCTRL, SMARTEN]

        data_int = []

        # Convert bitstrings to integer
        for bs in bs_list:
            bs = ''.join(bs.split()) # Split bitstring to list
            data_int.append(int(bs,2)) # Convert binary value string to integer (decimal)

        # Convert integer list to bytearray
        data = self.int_to_bytes(data_int)

        for d in data:
            tx = self.bytearray_to_bitstring(d)
            log.info("TX: {0}".format(tx))
            recvd = self.spi.xfer(d) # Send transfer and listen for answer
            rx = self.bytearray_to_bitstring(recvd)
            log.info("RX: {0}".format(rx))
            time.sleep(0.5)


    def readback(self):

        READBACK = "0100 0000 0000 0000 0000" # xxxxx

        rbck = ''.join(READBACK.split())
        rbck = int(rbck,2)
        data = self.int_to_bytes([rbck])

        rb = self.spi.xfer(data[0]) # Send transfer and listen for answer
        rb = self.bytearray_to_bitstring(rb)
        log.info("RBCK: {0}".format(rb))
        self.log_readback(rb)


    def spi_select(self, mot):
        """ Sets SPI selector pins and flag according to the selected motor. """

        if mot not in [1,2,3]:
            log.warning("Invalid motor selected! ({0})".format(mot))
            return

        smc.spi_select(mot)
        self.MOTOR = mot


    def bytearray_to_bitstring(self, bytearray):

        if bytearray == None:
            return None

        s = ""
        for b in bytearray:
            s += "{:08b}-".format(b)

        return s[4:-1]


    def log_readback(self, bitstring):
        """ Decodes the 20-bit long readback string from motor driver,
        and logs errors or warnings if any.
        """

        bitstring = bitstring.replace("-","")
        bitstring = bitstring.strip()

        motor = "Motor {0}: ".format(self.MOTOR)

        if bitstring[19] == "1": # SG
            log.warning(motor + "StallGuard2 threshold has been reached!")

        if bitstring[18] == "1": # OT
            log.critical(motor + "Overtemperature shutdown!")

        if bitstring[17] == "1": # OTPW
            log.warning(motor + "Overtemperature warning!")

        if (bitstring[16] == "1") or (bitstring[15] == "1"): # S2GA / S2GB
            log.critical(motor + "Short to GND condition" +
            " on high-side transistors!")

        if (bitstring[14] == "1") or (bitstring[13] == "1"): # OLA / OLB
            log.info(motor + "Open load condition!")

        if bitstring[12] == "1": # STST
            log.warning(motor + "Standstill condition!")


    def int_to_bytes(self, int_list):
        """ Convert a list of integers to a list '3-byte array'. """

        data = []

        for k in int_list:
            d = []
            # Convert hexa number to byte list / big-endian, 4-byte int
            b = list(struct.pack('>i',k))
            # Drop the first byte to make 3-byte list and add to data list
            for bi in b[1:]: d.append(int(bi))
            data.append(d)

        return data


    def close(self):
        self.spi.close()


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


    finally:
        print("Finished!")
