ECHO OFF
chcp 65001
cls


:loop
cls
pylint SPI_comm.py --output-format=colorized
pause
goto loop
