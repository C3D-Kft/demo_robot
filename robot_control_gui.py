# -*- coding: utf-8 -*-
# !/usr/bin/python3

""" GUI (frontend) a Demo robot vezérléshez. Ez a modul tartalmazza a
főképernyő grafikus interface elemeit.

---- Libs ----
* Tkinter
* Threading

---- Help ----
* https://effbot.org/tkinterbook/tkinter-events-and-bindings.htm
* https://pythonprogramming.net/tkinter-tutorial-python-3-event-handling/\
    ?completed=/tkinter-python-3-tutorial-adding-buttons/
* http://zetcode.com/tkinter/layout/
* http://www.science.smith.edu/dftwiki/index.php/Color_Charts_for_TKinter
* https://www.programcreek.com/python/example/16883/tkFileDialog.askdirectory
* https://stackoverflow.com/questions/22624962/python-threads-not-running\
    -in-parallel
* https://stackoverflow.com/questions/43683257/python-close-a-thread-\
    on-multithreading

---- Info ----
C3D Kft. - Minden jog fenntartva a birtoklásra, felhasználásra,
sokszorosításra, szerkesztésre, értékesítésre nézve, valamint az ipari
tulajdonjog hatálya alá eső felhasználások esetén is.
www.C3D.hu
"""

import logger
import logging
import os
import sys
import tkinter as tk
from tkinter import StringVar
from tkinter import filedialog
from enum import Enum
import threading
import robot_control as rcl
import SPI_comm
import data_collector as dcl


logger.init_logger()
log = logging.getLogger("Main")
log.info("Program started!")

# Global constants
INIT_DIRECTORY = os.path.abspath("/media/pi/")

# Init SPI
SPI = SPI_comm.SPI()


class MotorStatus(Enum):
    enabled = 1
    disabled = 0


class RecordEncodersStatus(Enum):
    disabled = 0
    recording = 1


class App:
    def __init__(self, master):

        self.master = master
        self.frame = tk.Frame(self.master)
        self.master.geometry("800x460+0-19")  # Ablak mérete +xpos(v)+ypos(f)
        self.master.resizable(width=False, height=False)
        self.master.title("Demo robot vezérlő")  # Ablak cím beállítása
        self.fty = "Arial"
        self.fsize = 20
        self.pos1 = StringVar()
        self.pos2 = StringVar()
        self.pos3 = StringVar()
        self.mode = rcl.Interpolation.MOD1
        self.motor_status = MotorStatus.enabled
        self.recording_status = RecordEncodersStatus.disabled

        # Initialize robot, GPIOs; switch on power
        rcl.init()
        log.info("GPIO initialization complete!")

        # Initialize SPI
        SPI.init()

        # Zeroing the robot
        rcl.zeroing()

        # Get abs. pos data, which should be null
        self.abs_pos = rcl.get_actual_abs_position()
        self.pos1.set("{0:+.2f}".format(self.abs_pos[0]))
        self.pos2.set("{0:+.2f}".format(self.abs_pos[1]))
        self.pos3.set("{0:+.2f}".format(self.abs_pos[2]))

        # Initialize window
        self.frame.grid()
        self.frame.grid_columnconfigure(0, minsize=300)
        self.frame.grid_columnconfigure(1, minsize=380)
        self.frame.grid_columnconfigure(2, minsize=120)
        self.frame.grid_rowconfigure(0, minsize=240)
        self.frame.grid_rowconfigure(1, minsize=220)

        actual_pos_panel = tk.LabelFrame(self.frame, text="Aktuális pozíció")
        actual_pos_panel.grid(
            row=0, column=0, sticky=tk.NSEW, padx=(5, 2.5), pady=(5, 2.5)
        )
        jog_panel = tk.LabelFrame(self.frame, text="Robotkar jogging")
        jog_panel.grid(
            row=0, column=1, sticky=tk.NSEW, padx=(2.5, 2.5), pady=(5, 2.5)
        )
        send_to_pos_panel = tk.LabelFrame(self.frame, text="Pozícióba küld")
        send_to_pos_panel.grid(
            row=1, column=0, sticky=tk.NSEW, padx=(5, 2.5), pady=(2.5, 5)
        )
        limit_panel = tk.LabelFrame(self.frame, text="Tengely limitek")
        limit_panel.grid(
            row=1, column=1, sticky=tk.NSEW, padx=(2.5, 2.5), pady=(2.5, 5)
        )
        menu_panel = tk.LabelFrame(self.frame, text="Menü")
        menu_panel.grid(
            row=0, rowspan=2, column=2, sticky=tk.NSEW,
            padx=(2.5, 5), pady=(5, 5)
        )

        # First grid
        actual_pos_panel.grid()
        act_pos_label_frame = tk.Frame(actual_pos_panel)
        act_pos_label_frame.grid(row=0, column=0, sticky=tk.NSEW)

        axis_1_label = tk.Label(
            act_pos_label_frame, text="Motor 1",
            font=(self.fty, self.fsize), anchor="w"
        )
        axis_1_label.grid(
            row=0, column=0, sticky=tk.EW, padx=(0, 10), pady=(0, 5)
        )
        axis_2_label = tk.Label(
            act_pos_label_frame, text="Motor 2",
            font=(self.fty, self.fsize), anchor="w"
        )
        axis_2_label.grid(
            row=1, column=0, sticky=tk.EW, padx=(0, 10), pady=(5, 5)
        )
        axis_3_label = tk.Label(
            act_pos_label_frame, text="Motor 3",
            font=(self.fty, self.fsize), anchor="w"
        )
        axis_3_label.grid(
            row=2, column=0, sticky=tk.EW, padx=(0, 10), pady=(5, 0)
        )

        self.axis_1_entry = tk.Entry(
            act_pos_label_frame, width=8, justify="right",
            font=(self.fty, self.fsize), textvariable=self.pos1
        )
        self.axis_1_entry.config(state=tk.DISABLED)
        self.axis_1_entry.grid(row=0, column=1, pady=(0, 5))

        self.axis_2_entry = tk.Entry(
            act_pos_label_frame, width=8, justify="right",
            font=(self.fty, self.fsize), textvariable=self.pos2
        )
        self.axis_2_entry.config(state=tk.DISABLED)
        self.axis_2_entry.grid(row=1, column=1, sticky=tk.EW, pady=(5, 5))

        self.axis_3_entry = tk.Entry(
            act_pos_label_frame, width=8, justify="right",
            font=(self.fty, self.fsize), textvariable=self.pos3
        )
        self.axis_3_entry.config(state=tk.DISABLED)
        self.axis_3_entry.grid(row=2, column=1, sticky=tk.EW, pady=(5, 0))

        axis_1_unit_label = tk.Label(
            act_pos_label_frame, text="fok", anchor="w",
            font=(self.fty, self.fsize)
        )
        axis_1_unit_label.grid(
            row=0, column=2, sticky=tk.EW, padx=(5, 0), pady=(0, 5))
        axis_2_unit_label = tk.Label(
            act_pos_label_frame, text="fok", anchor="w",
            font=(self.fty, self.fsize)
        )
        axis_2_unit_label.grid(
            row=1, column=2, sticky=tk.EW, padx=(5, 0), pady=(5, 5)
        )
        axis_3_unit_label = tk.Label(
            act_pos_label_frame, text="fok", anchor="w",
            font=(self.fty, self.fsize)
        )
        axis_3_unit_label.grid(
            row=2, column=2, sticky=tk.EW, padx=(5, 0), pady=(5, 0)
        )

        # Second grid
        send_to_pos_panel.grid()

        stp_label_frame = tk.Frame(send_to_pos_panel)
        stp_label_frame.grid(row=0, column=0, sticky=tk.NSEW)

        axis_1_label_stp = tk.Label(
            stp_label_frame, text="Motor 1",
            font=(self.fty, self.fsize), anchor="w"
        )
        axis_1_label_stp.grid(
            row=0, column=0, sticky=tk.EW, padx=(0, 10), pady=(0, 5)
        )
        axis_2_label_stp = tk.Label(
            stp_label_frame, text="Motor 2",
            font=(self.fty, self.fsize), anchor="w"
        )
        axis_2_label_stp.grid(
            row=1, column=0, sticky=tk.EW, padx=(0, 10), pady=(5, 5)
        )
        axis_3_label_stp = tk.Label(
            stp_label_frame, text="Motor 3",
            font=(self.fty, self.fsize), anchor="w"
        )
        axis_3_label_stp.grid(
            row=2, column=0, sticky=tk.EW, padx=(0, 10), pady=(5, 0)
        )

        self.axis_1_entry_stp = tk.Entry(
            stp_label_frame, width=8, justify="right",
            font=(self.fty, self.fsize)
        )
        self.axis_1_entry_stp.insert("0", "0")  # default érték
        self.axis_1_entry_stp.grid(row=0, column=1, pady=(0, 5))

        self.axis_2_entry_stp = tk.Entry(
            stp_label_frame, width=8, justify="right",
            font=(self.fty, self.fsize)
        )
        self.axis_2_entry_stp.insert("0", "0")
        self.axis_2_entry_stp.grid(row=1, column=1, sticky=tk.EW, pady=(5, 5))

        self.axis_3_entry_stp = tk.Entry(
            stp_label_frame, width=8,
            justify="right", font=(self.fty, self.fsize)
        )
        self.axis_3_entry_stp.insert("0", "0")
        self.axis_3_entry_stp.grid(row=2, column=1, sticky=tk.EW, pady=(5, 5))

        axis_1_unit_label_stp = tk.Label(
            stp_label_frame, text="fok", anchor="w", font=(self.fty, self.fsize)
        )
        axis_1_unit_label_stp.grid(
            row=0, column=2, sticky=tk.EW, padx=(5, 0), pady=(0, 5)
        )
        axis_2_unit_label_stp = tk.Label(
            stp_label_frame, text="fok", anchor="w", font=(self.fty, self.fsize)
        )
        axis_2_unit_label_stp.grid(
            row=1, column=2, sticky=tk.EW, padx=(5, 0), pady=(5, 5)
        )
        axis_3_unit_label_stp = tk.Label(
            stp_label_frame, text="fok", anchor="w", font=(self.fty, self.fsize)
        )
        axis_3_unit_label_stp.grid(
            row=2, column=2, sticky=tk.EW, padx=(5, 0), pady=(5, 5)
        )

        # Third grid
        jog_panel.grid()
        jog_panel.grid_columnconfigure(0, weight=1)
        jog_panel.grid_columnconfigure(1, weight=1)
        jog_panel.grid_columnconfigure(2, weight=1)
        jog_panel.grid_columnconfigure(3, weight=1)
        jog_panel.grid_rowconfigure(0, weight=4)
        jog_panel.grid_rowconfigure(1, weight=1)

        mot1_frame = tk.Frame(jog_panel)
        mot1_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=(5, 2.5))
        mot2_frame = tk.Frame(jog_panel)
        mot2_frame.grid(row=0, column=1, sticky=tk.NSEW, padx=2.5)
        mot3_frame = tk.Frame(jog_panel)
        mot3_frame.grid(row=0, column=2, sticky=tk.NSEW, padx=2.5)
        mot4_frame = tk.Frame(jog_panel)
        mot4_frame.grid(row=0, column=3, sticky=tk.NSEW, padx=(2.5, 5))

        self.fsize2 = 16  # Szöveg elsö sorban
        self.fsize3 = 16  # +,-,N karakterek

        mot1label = tk.Label(
            mot1_frame, text="Motor 1", font=(self.fty, self.fsize2)
        )
        mot1label.grid(row=0, column=0)
        self.mot1but1 = tk.Button(
            mot1_frame, text="+", font=(self.fty, self.fsize3)
        )
        self.mot1but1.grid(row=1, column=0, sticky=tk.EW)
        self.mot1but2 = tk.Button(
            mot1_frame, text="-", font=(self.fty, self.fsize3)
        )
        self.mot1but2.grid(row=2, column=0, sticky=tk.EW)
        self.mot1but3 = tk.Button(
            mot1_frame, text="N", command=lambda: self.reset_motor(0),
            font=(self.fty, self.fsize3)
        )
        self.mot1but3.grid(row=3, column=0, sticky=tk.EW)

        mot2label = tk.Label(
            mot2_frame, text="Motor 2", font=(self.fty, self.fsize2)
        )
        mot2label.grid(row=0, column=0)
        self.mot2but1 = tk.Button(
            mot2_frame, text="+", font=(self.fty, self.fsize3)
        )
        self.mot2but1.grid(row=1, column=0, sticky=tk.EW)
        self.mot2but2 = tk.Button(
            mot2_frame, text="-", font=(self.fty, self.fsize3)
        )
        self.mot2but2.grid(row=2, column=0, sticky=tk.EW)
        self.mot2but3 = tk.Button(
            mot2_frame, text="N", command=lambda: self.reset_motor(1),
            font=(self.fty, self.fsize3)
        )
        self.mot2but3.grid(row=3, column=0, sticky=tk.EW)

        mot3label = tk.Label(
            mot3_frame, text="Motor 3", font=(self.fty, self.fsize2)
        )
        mot3label.grid(row=0, column=0)
        self.mot3but1 = tk.Button(
            mot3_frame, text="+", font=(self.fty, self.fsize3)
        )
        self.mot3but1.grid(row=1, column=0, sticky=tk.EW)
        self.mot3but2 = tk.Button(
            mot3_frame, text="-", font=(self.fty, self.fsize3)
        )
        self.mot3but2.grid(row=2, column=0, sticky=tk.EW)
        self.mot3but3 = tk.Button(
            mot3_frame, text="N", command=lambda: self.reset_motor(2),
            font=(self.fty, self.fsize3)
        )
        self.mot3but3.grid(row=3, column=0, sticky=tk.EW)

        mot4label = tk.Label(
            mot4_frame, text="Gripper", font=(self.fty, self.fsize2)
        )
        mot4label.grid(row=0, column=0)
        self.mot4but1 = tk.Button(
            mot4_frame, text="+", command=self.grip_hold,
            font=(self.fty, self.fsize3)
        )
        self.mot4but1.grid(row=1, column=0, sticky=tk.EW)
        self.mot4but2 = tk.Button(
            mot4_frame, text="-", command=self.grip_release,
            font=(self.fty, self.fsize3)
        )
        self.mot4but2.grid(row=2, column=0, sticky=tk.EW)

        self.mot1but1.bind(
            '<ButtonPress-1>', lambda event: self.jog_motor(0, 1)
        )
        self.mot1but2.bind(
            '<ButtonPress-1>', lambda event: self.jog_motor(0, 0)
        )
        self.mot1but1.bind('<ButtonRelease-1>', self.stop_motor)
        self.mot1but2.bind('<ButtonRelease-1>', self.stop_motor)

        self.mot2but1.bind(
            '<ButtonPress-1>', lambda event: self.jog_motor(1, 1)
        )
        self.mot2but2.bind(
            '<ButtonPress-1>', lambda event: self.jog_motor(1, 0)
        )
        self.mot2but1.bind('<ButtonRelease-1>', self.stop_motor)
        self.mot2but2.bind('<ButtonRelease-1>', self.stop_motor)

        self.mot3but1.bind(
            '<ButtonPress-1>', lambda event: self.jog_motor(2, 1)
        )
        self.mot3but2.bind(
            '<ButtonPress-1>', lambda event: self.jog_motor(2, 0)
        )
        self.mot3but1.bind('<ButtonRelease-1>', self.stop_motor)
        self.mot3but2.bind('<ButtonRelease-1>', self.stop_motor)

        self.zero_but = tk.Button(
            jog_panel, text="ZERO", font=(self.fty, self.fsize3),
            command=self.zero
        )
        self.zero_but.grid(
            row=1, column=0, columnspan=4, sticky=tk.EW,
            padx=(5, 5), pady=(2.5, 5)
        )

        # Fourth grid
        limit_panel.grid()
        limit_panel.grid_columnconfigure(0, weight=1)
        limit_panel.grid_columnconfigure(1, weight=1)
        limit_panel.grid_columnconfigure(2, weight=1)
        limit_panel.grid_rowconfigure(0, weight=1)

        lim_mot1_frame = tk.Frame(limit_panel)
        lim_mot1_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=(5, 2.5))
        lim_mot2_frame = tk.Frame(limit_panel)
        lim_mot2_frame.grid(row=0, column=1, sticky=tk.NSEW, padx=2.5)
        lim_mot3_frame = tk.Frame(limit_panel)
        lim_mot3_frame.grid(row=0, column=2, sticky=tk.NSEW, padx=(2.5, 5))

        self.fsize2 = 16  # Szöveg elsö sorban
        self.fsize3 = 16  # +,-,N karakterek

        mot1lab = tk.Label(
            lim_mot1_frame, text="Motor 1", font=(self.fty, self.fsize)
        )
        mot1lab.grid(row=0, column=0)
        self.mot1ent1 = tk.Entry(
            lim_mot1_frame, width=7, justify="right",
            font=(self.fty, self.fsize)
        )
        self.mot1ent1.grid(row=1, column=0, sticky=tk.EW)
        self.mot1ent2 = tk.Entry(
            lim_mot1_frame, width=7, justify="right",
            font=(self.fty, self.fsize)
        )
        self.mot1ent2.grid(row=2, column=0, sticky=tk.EW)
        
        mot2lab = tk.Label(
            lim_mot2_frame, text="Motor 2", font=(self.fty, self.fsize)
        )
        mot2lab.grid(row=0, column=1)
        self.mot2ent1 = tk.Entry(
            lim_mot2_frame, width=7, justify="right",
            font=(self.fty, self.fsize)
        )
        self.mot2ent1.grid(row=1, column=1, sticky=tk.EW)
        self.mot2ent2 = tk.Entry(
            lim_mot2_frame, width=7, justify="right",
            font=(self.fty, self.fsize)
        )
        self.mot2ent2.grid(row=2, column=1, sticky=tk.EW)

        mot3lab = tk.Label(
            lim_mot3_frame, text="Motor 3", font=(self.fty, self.fsize)
        )
        mot3lab.grid(row=0, column=2)
        self.mot3ent1 = tk.Entry(
            lim_mot3_frame, width=7, justify="right",
            font=(self.fty, self.fsize)
        )
        self.mot3ent1.grid(row=1, column=2, sticky=tk.EW)
        self.mot3ent2 = tk.Entry(
            lim_mot3_frame, width=7,
            justify="right", font=(self.fty, self.fsize)
        )
        self.mot3ent2.grid(row=2, column=2, sticky=tk.EW)
        self.get_axis_limits()

        # Fifth panel
        menu_panel.grid()
        menu_button_frame = tk.Frame(menu_panel)
        menu_button_frame.grid(row=0, column=0, sticky=tk.NSEW)

        self.send_to_position_but = tk.Button(
            menu_button_frame, text="STRT", font=(self.fty, self.fsize),
            command=self.send_to_position
        )
        self.send_to_position_but.grid(
            row=0, column=0, sticky=tk.NSEW, pady=(5, 0), padx=2.5
        )
        self.follow_route_but = tk.Button(
            menu_button_frame, text="PROG", font=(self.fty, self.fsize),
            command=self.follow_route
        )
        self.follow_route_but.grid(
            row=1, column=0, sticky=tk.NSEW, pady=2.5, padx=2.5
        )
        self.mode_button = tk.Button(
            menu_button_frame, text=self.mode,
            font=(self.fty, self.fsize), command=self.change_interpolation_mode
        )
        self.mode_button.grid(
            row=2, column=0, sticky=tk.NSEW, pady=2.5, padx=2.5
        )
        self.enable_all_mot_but = tk.Button(
            menu_button_frame, text="DSBL", font=(self.fty, self.fsize),
            command=self.change_motor_status
        )
        self.enable_all_mot_but.grid(
            row=3, column=0, sticky=tk.NSEW, pady=2.5, padx=2.5
        )
        self.set_limits = tk.Button(
            menu_button_frame, text="SET", font=(self.fty, self.fsize),
            command=self.set_axis_limits
        )
        self.set_limits.grid(
            row=4, column=0, sticky=tk.NSEW, pady=2.5, padx=2.5
        )
        self.change_recording = tk.Button(
            menu_button_frame, text="REC", font=(self.fty, self.fsize),
            command=self.change_recording_status
        )
        self.change_recording.grid(
            row=5, column=0, sticky=tk.NSEW, pady=2.5, padx=2.5
        )

        self.close_win = tk.Button(
            menu_button_frame, text="EXIT",
            font=(self.fty, self.fsize), command=self.close_window
        )
        self.close_win.grid(
            row=6, column=0, sticky=tk.NSEW, pady=2.5, padx=2.5
        )

    def update_abs_pos_jog(self):
        """ Update abs. position when jogging! """

        while self.jog_thread.is_alive():
            root.after(10, self.update_abs_pos())
            root.after(10, root.update_idletasks())

    def jog_motor(self, mot, direction):
        rcl.JOGGING = True
        self.jog_thread = threading.Thread(
            target=rcl.jog,
            args=(mot, direction)
        )  # <-- check for syntax !!
        self.jog_thread.start()
        update_thread = threading.Thread(target=self.update_abs_pos_jog)
        update_thread.start()

    def stop_motor(self, event=None):
        rcl.JOGGING = False
        self.update_abs_pos()

    def reset_motor(self, mot):
        log.info("Motor%s reset!", mot+1)
        rcl.ACTUAL_ABS_POSITION[mot] = 0
        self.update_abs_pos()

    def zero(self):
        for k in range(0, 3):
            self.reset_motor(k)

    def update_abs_pos(self):
        """ Update actual motor positions, and then refresh entries. """
        self.abs_pos = rcl.get_actual_abs_position()
        self.pos1.set("{0:+.2f}".format(self.abs_pos[0]))
        self.pos2.set("{0:+.2f}".format(self.abs_pos[1]))
        self.pos3.set("{0:+.2f}".format(self.abs_pos[2]))

    def send_to_position(self):
        """ Convert user input to absolute deg. values to go. """

        self.send_to_position_but.config(state=tk.DISABLED)
        self.follow_route_but.config(state=tk.DISABLED)

        try:
            # Get values from Entry fields
            ga1 = float(self.axis_1_entry_stp.get())
            ga2 = float(self.axis_2_entry_stp.get())
            ga3 = float(self.axis_3_entry_stp.get())

            # Start secondary thread with move function
            secondary_thread = threading.Thread(
                target=rcl.move_absolute,
                args=([ga1, ga2, ga3], )
            )  # <-- check for syntax !!
            secondary_thread.start()

            # While sec. thread is running, pos is being updated 1 ms interval
            while secondary_thread.is_alive():
                root.after(10, self.update_abs_pos())
                root.after(10, root.update_idletasks())

            # Final update when move ended
            self.update_abs_pos()

        except:
            log.info("User input error!")

        finally:
            self.send_to_position_but.config(state='normal')
            self.follow_route_but.config(state='normal')

    def follow_route(self):
        """ Opens a given .grt (CREO Graph Report) file. """

        global INIT_DIRECTORY

        data = [[], [], []]

        # TODO: Implement multiple file selection (?)
        filename = filedialog.askopenfilenames(
            initialdir=INIT_DIRECTORY, title='Kiválasztás',
            filetypes=[
                    ("GRT file format", ".grt"),
                ]
        )

        # Ha Cancel-lel kilépek
        if filename == "":
            log.info("No file selected!")
            return

        # Attempt to read data
        try:
            filename = filename[0]
            log.info("Opening file: %s", os.path.relpath(filename))

            INIT_DIRECTORY = os.path.dirname(filename)

            # Kiolvasom a fájl tartalmát
            with open(filename, "r", encoding="cp437", errors='ignore') as inpt:
                lines = inpt.readlines()
            # Processing
            log.info("Processing %s graph!", lines[0][1:-2])

            motor_axis = 0
            for line in lines[4:]:
                # Ha a sor tartalma: 'plot', ugrok a következő motor tengelyre
                if line[0:4] == "plot":
                    motor_axis += 1
                    continue

                # Last element is '/n' (newline character)
                k = line.split("\t")[:-1]
                data[motor_axis].append(float(k[1]))

            # When success
            log.info("File has been successfully opened!")

        except FileNotFoundError:
            log.error("%s not found!", filename.capitalize())

        except:
            log.critical("Unexpected error: %s", sys.exc_info()[0])
            raise

        # Attempt to move to given positions
        self.send_to_position_but.config(state=tk.DISABLED)
        self.follow_route_but.config(state=tk.DISABLED)

        try:
            # Start secondary thread with move function
            secondary_thread = threading.Thread(
                target=self.move_absolute_loop, args=([data])
            )  # <-- check for syntax !!
            secondary_thread.start()

            # While sec. thread is running, pos is being updated 1 ms interval
            while secondary_thread.is_alive():
                root.after(10, self.update_abs_pos())
                root.after(10, root.update_idletasks())

            # Final update when move ended
            self.update_abs_pos()

        except:
            log.critical("Unexpected error occurred!")

        finally:
            self.send_to_position_but.config(state='normal')
            self.follow_route_but.config(state='normal')

    def move_absolute_loop(self, data):
        """ Iterates over an absolute move list. """

        position_list = []
        for i in range(0, len(data[0])):
            position_list.append(
                [data[0][i], data[1][i], data[2][i]]
            )

        rcl.move_absolute_loop(position_list)

    def grip_release(self):
        rcl.grip_release()  # 180 fokos fordulat egyik irányba
        log.info("Grip released!")

    def grip_hold(self):
        rcl.grip_hold()  # 180 fokos fordulat másik irányba
        log.info("Grip hold!")

    def change_interpolation_mode(self):

        if self.mode == rcl.Interpolation.MOD1:
            self.mode = rcl.Interpolation.MOD2
        else:
            self.mode = rcl.Interpolation.MOD1

        self.mode_button['text'] = "{0}".format(self.mode)
        rcl.switch_mode("{0}".format(self.mode))
        log.info("Change interpolation mode to: %s", self.mode)

    def change_motor_status(self):
        if self.motor_status is MotorStatus.enabled:
            log.info("Disable all motors!")
            self.motor_status = MotorStatus.disabled
            rcl.motor_enable_set(1)
            self.enable_all_mot_but["text"] = "ENBL"

        else:
            log.info("Enable all motors!")
            self.motor_status = MotorStatus.enabled
            rcl.motor_enable_set(0)
            self.enable_all_mot_but["text"] = "DSBL"

    def change_recording_status(self):
        if self.recording_status is RecordEncodersStatus.disabled:
            log.info("Start recording")
            self.recording_status = RecordEncodersStatus.recording
            # collect data
            self.change_recording["text"] = "STOP"
        else:
            log.info("Stop recording")
            self.recording_status = RecordEncodersStatus.disabled
            # stop collecting data
            self.change_recording["text"] = "REC"

    def set_axis_limits(self):
        """ Tengely limitek beállítása a programban. """

        min_lim, max_lim = rcl.get_limits()
        a1_max = float(self.mot1ent1.get())
        a1_min = float(self.mot1ent2.get())
        a2_max = float(self.mot2ent1.get())
        a2_min = float(self.mot2ent2.get())
        a3_max = float(self.mot3ent1.get())
        a3_min = float(self.mot3ent2.get())

        if a1_max >= a1_min:
            min_lim[0] = a1_min
            max_lim[0] = a1_max
        else:
            log.info("Axis 1 limits doesn't changed!")

        if a2_max >= a2_min:
            min_lim[1] = a2_min
            max_lim[1] = a2_max
        else:
            log.info("Axis 2 limits doesn't changed!")

        if a3_max >= a3_min:
            min_lim[2] = a3_min
            max_lim[2] = a3_max
        else:
            log.info("Axis 3 limits doesn't changed!")

        rcl.set_limits(min_lim, max_lim)
        self.get_axis_limits()

    def get_axis_limits(self):
        """ Tengely limitek beállítása a képernyőn. """

        min_lim, max_lim = rcl.get_limits()
        self.mot1ent1.delete(0, 'end')
        self.mot1ent2.delete(0, 'end')
        self.mot2ent1.delete(0, 'end')
        self.mot2ent2.delete(0, 'end')
        self.mot3ent1.delete(0, 'end')
        self.mot3ent2.delete(0, 'end')

        self.mot1ent1.insert("0", max_lim[0])
        self.mot1ent2.insert("0", min_lim[0])
        self.mot2ent1.insert("0", max_lim[1])
        self.mot2ent2.insert("0", min_lim[1])
        self.mot3ent1.insert("0", max_lim[2])
        self.mot3ent2.insert("0", min_lim[2])

    def close_window(self):
        """ Ablak bezárása. """
        self.master.destroy()
        log.info("Main window terminated!")


# Main program
if __name__ == '__main__':

    # Login window init
    root = tk.Tk()
    main_prog = App(root)
    # 'X' gomb felülírása
    root.wm_protocol('WM_DELETE_WINDOW', main_prog.close_window)
    root.mainloop()

    SPI.close()
    rcl.poweroff()
    rcl.cleanup()
    log.info("Program exit!")
    sys.exit()
