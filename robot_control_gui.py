# -*- coding: utf-8 -*-
#!/usr/bin/python3

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


# Logolás inicializálása
import logging
import logger

logger.init_logger()
log = logging.getLogger("Main")
log.info("Program started!")

# Modulok betöltése a logolás indítása után!
import os
import sys
import tkinter as tk
from tkinter import StringVar
from tkinter import filedialog
import threading
import robot_control as RC

# Globális változók
if getattr(sys, 'frozen', False):
    initdir = os.path.dirname(sys.executable)
elif __file__:
    initdir = os.path.dirname(__file__)


class App():
    def __init__(self, master):
        self.master = master
        self.frame = tk.Frame(self.master)
        self.master.geometry("700x480+200+200") #Ablak mérete +xpos(v)+ypos(f)
        self.master.resizable(width=False, height=False)
        # self.master.attributes('-fullscreen', True)
        self.master.title("Demo robot vezérlő") # Ablak cím beállítása

        self.fs="Arial"
        self.fsize=20

        self.pos1 = StringVar()
        self.pos2 = StringVar()
        self.pos3 = StringVar()

        # Initialize robot
        RC.init()

        # Zeroing the robot
        RC.zeroing()

        # Get abs. pos data, which should be null
        self.abs_pos = RC.get_actual_abs_position()
        self.pos1.set("{0:+.2f}".format(self.abs_pos[0]))
        self.pos2.set("{0:+.2f}".format(self.abs_pos[1]))
        self.pos3.set("{0:+.2f}".format(self.abs_pos[2]))

        self.init_window() # Inicializáló fv. meghívása


    # Init_window létrehozása (konstruktor)
    def init_window(self):

        self.frame.grid()
        self.frame.grid_columnconfigure(0, minsize=300)
        self.frame.grid_columnconfigure(1, minsize=400)
        self.frame.grid_rowconfigure(0, minsize=240)
        self.frame.grid_rowconfigure(1, minsize=240)

        actual_pos_panel = tk.LabelFrame(self.frame, text="Aktuális pozíció")
        actual_pos_panel.grid(row = 0, column = 0, sticky = 'NWSE',
        padx = (5,2.5), pady = (5,2.5))

        jog_panel = tk.LabelFrame(self.frame, text="Robotkar jogging")
        jog_panel.grid(row = 0, column = 1, sticky = 'NWSE',
        padx = (2.5,5), pady = (5,2.5))

        send_to_pos_panel = tk.LabelFrame(self.frame,
        text="Pozícióba küld")
        send_to_pos_panel.grid(row = 1, column = 0, sticky = 'NWSE',
        padx = (5,2.5), pady = (2.5,5))

        limit_panel = tk.LabelFrame(self.frame, text="Tengely limitek")
        limit_panel.grid(row = 1, column = 1, sticky = 'NWSE',
        padx = (2.5,5), pady = (2.5,5))


        # First grid
        actual_pos_panel.grid()

        axis_1_label = tk.Label(actual_pos_panel, text="Motor 1",
        font=(self.fs, self.fsize), anchor="w")
        axis_1_label.grid(row = 0, column = 0, sticky = 'WE',
        padx=(0,10), pady=(0,5))
        axis_2_label = tk.Label(actual_pos_panel, text="Motor 2",
        font=(self.fs, self.fsize), anchor="w")
        axis_2_label.grid(row = 1, column = 0, sticky = 'WE',
        padx=(0,10), pady=(5,5))
        axis_3_label = tk.Label(actual_pos_panel, text="Motor 3",
        font=(self.fs, self.fsize), anchor="w")
        axis_3_label.grid(row = 2, column = 0, sticky = 'WE',
        padx=(0,10), pady=(5,0))

        self.axis_1_entry = tk.Entry(actual_pos_panel, width=8,
        justify="right", font=(self.fs, self.fsize), textvariable=self.pos1)
        self.axis_1_entry.config(state= 'disabled')
        self.axis_1_entry.grid(row = 0, column = 1, pady=(0,5))

        self.axis_2_entry = tk.Entry(actual_pos_panel, width=8,
        justify="right", font=(self.fs, self.fsize), textvariable=self.pos2)
        self.axis_2_entry.config(state= 'disabled')
        self.axis_2_entry.grid(row = 1, column = 1, sticky = 'WE', pady=(5,5))

        self.axis_3_entry = tk.Entry(actual_pos_panel, width=8,
        justify="right", font=(self.fs, self.fsize), textvariable=self.pos3)
        self.axis_3_entry.config(state= 'disabled')
        self.axis_3_entry.grid(row = 2, column = 1, sticky = 'WE', pady=(5,0))

        axis_1_unit_label = tk.Label(actual_pos_panel, text="fok",
        anchor="w", font=(self.fs, self.fsize))
        axis_1_unit_label.grid(row = 0, column = 2, sticky = 'WE',
        padx=(5,0), pady=(0,5))
        axis_2_unit_label = tk.Label(actual_pos_panel, text="fok",
        anchor="w", font=(self.fs, self.fsize))
        axis_2_unit_label.grid(row = 1, column = 2, sticky = 'WE',
        padx=(5,0), pady=(5,5))
        axis_3_unit_label = tk.Label(actual_pos_panel, text="fok",
        anchor="w", font=(self.fs, self.fsize))
        axis_3_unit_label.grid(row = 2, column = 2, sticky = 'WE',
        padx=(5,0), pady=(5,0))


        # Second grid
        send_to_pos_panel.grid()

        stp_label_frame = tk.Frame(send_to_pos_panel)
        stp_label_frame.grid(row = 0, column = 0, sticky = 'NWSE')

        axis_1_label_stp = tk.Label(stp_label_frame, text="Motor 1",
        font=(self.fs, self.fsize), anchor="w")
        axis_1_label_stp.grid(row = 0, column = 0, sticky = 'WE',
        padx=(0,10), pady=(0,5))
        axis_2_label_stp = tk.Label(stp_label_frame, text="Motor 2",
        font=(self.fs, self.fsize), anchor="w")
        axis_2_label_stp.grid(row = 1, column = 0, sticky = 'WE',
        padx=(0,10), pady=(5,5))
        axis_3_label_stp = tk.Label(stp_label_frame, text="Motor 3",
        font=(self.fs, self.fsize), anchor="w")
        axis_3_label_stp.grid(row = 2, column = 0, sticky = 'WE',
        padx=(0,10), pady=(5,5))

        self.axis_1_entry_stp = tk.Entry(stp_label_frame, width=8,
        justify="right", font=(self.fs, self.fsize))
        self.axis_1_entry_stp.insert("0", "0") # default érték
        self.axis_1_entry_stp.grid(row = 0, column = 1, pady=(0,5))

        self.axis_2_entry_stp = tk.Entry(stp_label_frame, width=8,
        justify="right", font=(self.fs, self.fsize))
        self.axis_2_entry_stp.insert("0", "0")
        self.axis_2_entry_stp.grid(row = 1, column = 1, sticky = 'WE',
        pady=(5,5))

        self.axis_3_entry_stp = tk.Entry(stp_label_frame, width=8,
        justify="right", font=(self.fs, self.fsize))
        self.axis_3_entry_stp.insert("0", "0")
        self.axis_3_entry_stp.grid(row = 2, column = 1, sticky = 'WE',
        pady=(5,5))

        axis_1_unit_label_stp = tk.Label(stp_label_frame, text="fok",
        anchor="w", font=(self.fs, self.fsize))
        axis_1_unit_label_stp.grid(row = 0, column = 2, sticky = 'WE',
        padx=(5,0), pady=(0,5))
        axis_2_unit_label_stp = tk.Label(stp_label_frame, text="fok",
        anchor="w", font=(self.fs, self.fsize))
        axis_2_unit_label_stp.grid(row = 1, column = 2, sticky = 'WE',
        padx=(5,0), pady=(5,5))
        axis_3_unit_label_stp = tk.Label(stp_label_frame, text="fok",
        anchor="w", font=(self.fs, self.fsize))
        axis_3_unit_label_stp.grid(row = 2, column = 2, sticky = 'WE',
        padx=(5,0), pady=(5,5))

        stp_button_frame = tk.Frame(send_to_pos_panel)
        stp_button_frame.grid(row = 1, column = 0, sticky = 'NWSE')
        stp_button_frame.grid_columnconfigure(0, weight=1)
        stp_button_frame.grid_columnconfigure(1, weight=1)

        self.send_to_position = tk.Button(stp_button_frame, text="Start",
        font=(self.fs, self.fsize), command=self.send_to_position)
        self.send_to_position.grid(row=0, column=0, sticky = "NWSE",
        pady=(5,0), padx=(2.5,2.5))

        self.follow_route = tk.Button(stp_button_frame, text="Program",
        font=(self.fs, self.fsize), command=self.follow_route)
        self.follow_route.grid(row=0, column=1, sticky = "NWSE",
        pady=(5,0), padx=(2.5,2.5))

        # Third grid
        jog_panel.grid()
        jog_panel.grid_columnconfigure(0, weight=1)
        jog_panel.grid_columnconfigure(1, weight=1)
        jog_panel.grid_columnconfigure(2, weight=1)
        jog_panel.grid_columnconfigure(3, weight=1)
        jog_panel.grid_rowconfigure(0, weight=4)
        jog_panel.grid_rowconfigure(1, weight=1)

        mot1_frame = tk.Frame(jog_panel)
        mot1_frame.grid(row = 0, column = 0, sticky = 'NWSE', padx=(5,2.5))
        mot2_frame = tk.Frame(jog_panel)
        mot2_frame.grid(row = 0, column = 1, sticky = 'NWSE', padx=2.5)
        mot3_frame = tk.Frame(jog_panel)
        mot3_frame.grid(row = 0, column = 2, sticky = 'NWSE', padx=2.5)
        mot4_frame = tk.Frame(jog_panel)
        mot4_frame.grid(row = 0, column = 3, sticky = 'NWSE', padx=(2.5,5))

        self.fsize2 = 18
        self.fsize3 = 18

        mot1label = tk.Label(mot1_frame, text="Motor 1", font=(self.fs, self.fsize2))
        mot1label.grid(row=0, column=0)
        self.mot1but1 = tk.Button(mot1_frame, text="+", font=(self.fs, self.fsize3))
        self.mot1but1.grid(row=1, column=0, sticky="WE")
        self.mot1but2 = tk.Button(mot1_frame, text="-", font=(self.fs, self.fsize3))
        self.mot1but2.grid(row=2, column=0, sticky="WE")
        self.mot1but3 = tk.Button(mot1_frame, text="N",
        command=lambda:self.reset_motor(0), font=(self.fs, self.fsize3))
        self.mot1but3.grid(row=3, column=0, sticky="WE")

        mot2label = tk.Label(mot2_frame, text="Motor 2", font=(self.fs, self.fsize2))
        mot2label.grid(row=0, column=0)
        self.mot2but1 = tk.Button(mot2_frame, text="+", font=(self.fs, self.fsize3))
        self.mot2but1.grid(row=1, column=0, sticky="WE")
        self.mot2but2 = tk.Button(mot2_frame, text="-", font=(self.fs, self.fsize3))
        self.mot2but2.grid(row=2, column=0, sticky="WE")
        self.mot2but3 = tk.Button(mot2_frame, text="N",
        command=lambda:self.reset_motor(1), font=(self.fs, self.fsize3))
        self.mot2but3.grid(row=3, column=0, sticky="WE")

        mot3label = tk.Label(mot3_frame, text="Motor 3", font=(self.fs, self.fsize2))
        mot3label.grid(row=0, column=0)
        self.mot3but1 = tk.Button(mot3_frame, text="+", font=(self.fs, self.fsize3))
        self.mot3but1.grid(row=1, column=0, sticky="WE")
        self.mot3but2 = tk.Button(mot3_frame, text="-", font=(self.fs, self.fsize3))
        self.mot3but2.grid(row=2, column=0, sticky="WE")
        self.mot3but3 = tk.Button(mot3_frame, text="N",
        command=lambda:self.reset_motor(2), font=(self.fs, self.fsize3))
        self.mot3but3.grid(row=3, column=0, sticky="WE")

        mot4label = tk.Label(mot4_frame, text="Gripper", font=(self.fs, self.fsize2))
        mot4label.grid(row=0, column=0)
        self.mot4but1 = tk.Button(mot4_frame, text="+", command=self.grip_hold,
        font=(self.fs, self.fsize3))
        self.mot4but1.grid(row=1, column=0, sticky="WE")
        self.mot4but2 = tk.Button(mot4_frame, text="-", command=self.grip_release,
        font=(self.fs, self.fsize3))
        self.mot4but2.grid(row=2, column=0, sticky="WE")

        self.mot1but1.bind('<ButtonPress-1>', lambda event: self.jog_motor(0,1))
        self.mot1but2.bind('<ButtonPress-1>', lambda event: self.jog_motor(0,0))
        self.mot1but1.bind('<ButtonRelease-1>', self.stop_motor)
        self.mot1but2.bind('<ButtonRelease-1>', self.stop_motor)

        self.mot2but1.bind('<ButtonPress-1>', lambda event: self.jog_motor(1,1))
        self.mot2but2.bind('<ButtonPress-1>', lambda event: self.jog_motor(1,0))
        self.mot2but1.bind('<ButtonRelease-1>', self.stop_motor)
        self.mot2but2.bind('<ButtonRelease-1>', self.stop_motor)

        self.mot3but1.bind('<ButtonPress-1>', lambda event: self.jog_motor(2,1))
        self.mot3but2.bind('<ButtonPress-1>', lambda event: self.jog_motor(2,0))
        self.mot3but1.bind('<ButtonRelease-1>', self.stop_motor)
        self.mot3but2.bind('<ButtonRelease-1>', self.stop_motor)

        self.zero_but = tk.Button(jog_panel, text="ZERO",
        font=(self.fs, self.fsize3), command=self.zero)
        self.zero_but.grid(row=1, column=0, columnspan=4, sticky="WE",
        padx=(5,5), pady=(2.5, 5))


        # Fourth grid
        limit_panel.grid()

        mot1lab = tk.Label(limit_panel, text="Motor 1", font=(self.fs, self.fsize))
        mot1lab.grid(row=0, column=0, padx=(5,5), pady=(0,5))
        self.mot1ent1 = tk.Entry(limit_panel, width=7,
        justify="right", font=(self.fs, self.fsize))
        self.mot1ent1.grid(row=1, column=0, sticky="WE", padx=(5,5), pady=(0,5))
        self.mot1ent2 = tk.Entry(limit_panel, width=7,
        justify="right", font=(self.fs, self.fsize))
        self.mot1ent2.grid(row=2, column=0, sticky="WE", padx=(5,5), pady=(0,5))

        mot2lab = tk.Label(limit_panel, text="Motor 2", font=(self.fs, self.fsize))
        mot2lab.grid(row=0, column=1, padx=5, pady=(0,5))
        self.mot2ent1 = tk.Entry(limit_panel, width=7,
        justify="right", font=(self.fs, self.fsize))
        self.mot2ent1.grid(row=1, column=1, sticky="WE", padx=(0,5), pady=(0,5))
        self.mot2ent2 = tk.Entry(limit_panel, width=7,
        justify="right", font=(self.fs, self.fsize))
        self.mot2ent2.grid(row=2, column=1, sticky="WE", padx=(0,5), pady=(0,5))

        mot3lab = tk.Label(limit_panel, text="Motor 3", font=(self.fs, self.fsize))
        mot3lab.grid(row=0, column=2, padx=5, pady=(0,5))
        self.mot3ent1 = tk.Entry(limit_panel, width=7,
        justify="right", font=(self.fs, self.fsize))
        self.mot3ent1.grid(row=1, column=2, sticky="WE", padx=(0,5), pady=(0,5))
        self.mot3ent2 = tk.Entry(limit_panel, width=7,
        justify="right", font=(self.fs, self.fsize))
        self.mot3ent2.grid(row=2, column=2, sticky="WE", padx=(0,5), pady=(0,5))

        self.get_axis_limits()

        self.set_limits = tk.Button(limit_panel, text="Beállítás",
        font=(self.fs, self.fsize), command=self.set_axis_limits)
        self.set_limits.grid(row=3, column=0, columnspan=3, padx=(5,5), pady=(0,5))


    def update_abs_pos_jog(self, mot):
        """ Update abs. position when jogging! """

        while self.jog_thread.is_alive():
            root.after(10, self.update_abs_pos(mot))
            root.after(10, root.update_idletasks())


    def jog_motor(self, mot, dir):

        RC.jogging = True

        self.jog_thread = threading.Thread(target=RC.jog,
        args=(mot, dir )) # <-- check for syntax !!
        self.jog_thread.start()

        self.update_thread = threading.Thread(target=self.update_abs_pos_jog,
        args=(mot, ))
        self.update_thread.start()


    def stop_motor(self, event=None):
        RC.jogging = False
        self.update_abs_pos()
        log.info("Jogging stopped!")


    def reset_motor(self, mot):
        log.info("Motor{0} reset!".format(mot+1))
        RC.actual_abs_position[mot] = 0
        self.update_abs_pos()


    def zero(self):
        for k in range(0,3):
            self.reset_motor(k)


    def update_abs_pos(self, mot=None):
        """ Update actual motor positions, and then refresh entries. """

        self.abs_pos = RC.get_actual_abs_position()
        self.pos1.set("{0:+.2f}".format(self.abs_pos[0]))
        self.pos2.set("{0:+.2f}".format(self.abs_pos[1]))
        self.pos3.set("{0:+.2f}".format(self.abs_pos[2]))


    def send_to_position(self):
        """ Convert user input to absolute deg. values to go. """

        self.send_to_position.config(state='disabled')

        try:
            # Get values from Entry fields
            g1 = float(self.axis_1_entry_stp.get())
            g2 = float(self.axis_2_entry_stp.get())
            g3 = float(self.axis_3_entry_stp.get())

            # Start secondary thread with move function
            self.secondary_thread = threading.Thread(target=RC.move_absolute,
            args=([g1, g2, g3], )) # <-- check for syntax !!
            self.secondary_thread.start()

            # While sec. thread is running, pos is being updated 1 ms interval
            while self.secondary_thread.is_alive():
                root.after(1, self.update_abs_pos())
                root.after(1, root.update_idletasks())

            # Final update when move ended
            self.update_abs_pos()

        except:
            log.info("User input error!")

        finally:
            self.send_to_position.config(state='normal')


    def follow_route(self):
        """ Opens a given .txt file. """

        global initdir

        file = filedialog.askopenfilenames(initialdir=initdir,
        title='Kiválasztás', filetypes=[
                    ("TXT file format", ".txt"),
                ])

        # Ha Cancel-lel kilépek
        if file == "":
            log.info("No file selected!")
            return

        try:
            log.info("Opening file: {0}".format(file)) # Kiolvasom a fájl tartalmát
            with open(filename, "r", encoding="cp437", errors='ignore') as input:
                lines = input.readlines()

            # Read graphical data

            # Processing

            # When success
            log.info("File has been successfully opened!")

            return

        except FileNotFoundError as fnfe:
            log.error("{0} not found!".format(filename).capitalize())
            pass

        except:
            log.critical("Unexpected error: {0}".format(sys.exc_info()[0]))
            raise


    def grip_release(self):
        print("grip_release")


    def grip_hold(self):
        print("grip_hold")


    def set_axis_limits(self):
        """ Tengely limitek beállítása a programban. """

        min, max = RC.get_limits()

        a1_max = float(self.mot1ent1.get())
        a1_min = float(self.mot1ent2.get())
        a2_max = float(self.mot2ent1.get())
        a2_min = float(self.mot2ent2.get())
        a3_max = float(self.mot3ent1.get())
        a3_min = float(self.mot3ent2.get())

        if a1_max >= a1_min:
            min[0] = a1_min
            max[0] = a1_max
        else:
            print("Axis 1 limits doesn't changed!")

        if a2_max >= a2_min:
            min[1] = a2_min
            max[1] = a2_max
        else:
            print("Axis 2 limits doesn't changed!")

        if a3_max >= a3_min:
            min[2] = a3_min
            max[2] = a3_max
        else:
            print("Axis 3 limits doesn't changed!")

        RC.set_limits(min, max)

        self.get_axis_limits()


    def get_axis_limits(self):
        """ Tengely limitek beállítása a képernyőn. """

        min, max = RC.get_limits()

        self.mot1ent1.delete(0, 'end')
        self.mot1ent2.delete(0, 'end')
        self.mot2ent1.delete(0, 'end')
        self.mot2ent2.delete(0, 'end')
        self.mot3ent1.delete(0, 'end')
        self.mot3ent2.delete(0, 'end')

        self.mot1ent1.insert("0", max[0])
        self.mot1ent2.insert("0", min[0])
        self.mot2ent1.insert("0", max[1])
        self.mot2ent2.insert("0", min[1])
        self.mot3ent1.insert("0", max[2])
        self.mot3ent2.insert("0", min[2])


    def help(self):
        """ Segítség ablak megnyitása. """
        help_Window = tk.Toplevel(self.master)
        self.help_window = Help_window(help_Window)


    def close_window(self):
        """ Ablak bezárása. """
        self.master.destroy()
        print("Main window terminated!")


# Főprogram
if __name__ == '__main__':

    # Login window init
    root = tk.Tk()
    main_prog = App(root)
    # 'X' gomb felülírása
    root.wm_protocol('WM_DELETE_WINDOW', main_prog.close_window)
    root.mainloop()

    RC.cleanup()
    print("Program exit!")
    sys.exit()
