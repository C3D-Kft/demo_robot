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
from queue import Queue

log = logging.getLogger("Main")
que = Queue()
FLAG = False


def main():
    ser = serial.Serial('COM11', 9600, timeout=5)

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

    with open(filename, "w") as file:

        while not que.empty():  # Writing data to a file
            string = que.get().decode('utf-8').rstrip()
            file.write(f"{string}\n")  # Empties the queue

        log.info("File saved!")
