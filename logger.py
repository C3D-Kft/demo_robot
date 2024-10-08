# -*- coding: utf-8 -*-
# !/usr/bin/python3

""" Logger modul. A modul tartalmazza a naplózó beállításait. A naplózó
egyidejűleg az öt utolsó használat közben keletkezett naplófájlt örzi meg,
ezután újrahasználja azokat.

    * init_logger - naplózó inicializálása

---- Libs ----
* logging

---- Help ----
* https://www.toptal.com/python/in-depth-python-logging
* https://stackoverflow.com/questions/404744/determining-application-path\
-in-a-python-exe-generated-by-pyinstaller

---- Info ----
C3D Kft. - Minden jog fenntartva a birtoklásra, felhasználásra,
sokszorosításra, szerkesztésre, értékesítésre nézve, valamint az ipari
tulajdonjog hatálya alá eső felhasználások esetén is.
www.C3D.hu
"""


import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Globális változók beállítása
log_dirpath = Path("log")
log_filename = Path("main.txt")
init_directory = Path(__file__).parents[0]

# Ha a naplófájl mappa hiányzik, létrehozom
folderpath = Path.joinpath(init_directory, log_dirpath)
if not folderpath.is_dir():
    folderpath.mkdir()

log_file = Path.joinpath(init_directory, log_dirpath, log_filename)
FORMATTER = logging.Formatter(
    '%(asctime)s %(module)s [%(levelname)s] : %(message)s',
    datefmt='%Y/%m/%d %H:%M:%S'
)


def init_logger():
    logger = logging.getLogger("Main")
    logger.setLevel(logging.DEBUG)

    # Nincs felső byte limit - max. 5 indítás logját tartalmazza
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(FORMATTER)
    logger.addHandler(console_handler)

    file_handler = RotatingFileHandler(log_file, maxBytes=0, backupCount=5)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(FORMATTER)
    logger.addHandler(file_handler)  # Format, és file handler beállítások
    file_handler.doRollover()  # Átforgatja a logot minden indításnál
    logger.info("Logger created!")


def main():
    pass


# Modul-teszt
if __name__ == "__main__":
    main()
