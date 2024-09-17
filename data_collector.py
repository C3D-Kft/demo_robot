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
import threading
import serial
import platform
from queue import Queue

log = logging.getLogger("Main")
que = Queue()
FLAG = False

log.info("System detected: {0}".format(platform.system()))
if platform.system() == "Windows":
    serial_port = 'COM11'
elif platform.system() == "Linux":
    serial_port = '/dev/ttyACM0'
    # ‘/dev/ttyACM0’
baud_rate = 9600


def main():
    # NOTE: Arduino restarts when a new serial comm. is initiated
    ser = serial.Serial(serial_port, baud_rate, timeout=5)
    while True:
        read_serial = ser.readline()
        que.put(read_serial)
        log.info(read_serial)
        if not FLAG:
            break


def start_collect():
    global FLAG
    FLAG = True
    secondary_thread = threading.Thread(target=main)
    secondary_thread.start()


def stop_collect():
    global FLAG
    FLAG = False


def save_data(filename):
    """ Write the contents of the queue to a specified file. """

    with open(filename, "w") as file:
        found = False
        log.info("Start processing queue...")
        while not que.empty():  # Writing data to a file
            # NOTE: Arduino serial uses 'raw' encoding, it is defined by the
            #  code itself
            # NOTE: Decoding errors are ignored, otherwise the code breaks
            string = que.get().decode("ascii", "ignore")
            log.info("Processing: {0}".format(string.rstrip()))
            log.debug("Found: {0}".format(found))

            # Search for header, and ignore all lines before that
            if not found:
                idx = string.find("Set")
                log.debug("Found 'Set': {0}".format(idx))
                if idx != -1:
                    found = True

            if found:
                file.write(f"{string}")  # Empties the queue

        log.info("File saved!")

