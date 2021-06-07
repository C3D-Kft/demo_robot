# -*- coding: utf-8 -*-
#!/usr/bin/python3

""" GUI (frontend) a Demo robot vezérléshez. Ez a modul tartalmazza a
főképernyő grafikus interface elemeit.

    * App(class) - főprogram ablak
        * init_window - ablak grafikai kinézete
        * create - torna (szekvencia) összeállító ablak meghívása


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


print("Program started!")

# Modulok betöltése a logolás indítása után!
# import time
import os
import sys
# import math
from tkinter import ttk
import tkinter as tk
# from tkinter import StringVar
import threading
# import queue
import robot_control as RC


# Globális változók


class App():
    def __init__(self, master):
        self.master = master
        self.frame = tk.Frame(self.master)
        self.master.geometry("800x480+200+200") #Ablak mérete +xpos(v)+ypos(f)
        self.master.resizable(width=False, height=False)
        # self.master.attributes('-fullscreen', True)
        self.master.title("Demo robot control") # Ablak cím beállítása

        self.fs="Arial"
        self.fsize=20

        # Zeroing the robot
        RC.zeroing()
        # Get abs. pos data, which should be null
        self.abs_pos = RC.get_actual_abs_position()

        self.init_window() # Inicializáló fv. meghívása


    # Init_window létrehozása (konstruktor)
    def init_window(self):

        self.frame.grid()
        self.frame.grid_columnconfigure(0, minsize=300)
        self.frame.grid_columnconfigure(1, minsize=500)
        self.frame.grid_rowconfigure(0, minsize=240)
        self.frame.grid_rowconfigure(1, minsize=240)

        style = ttk.Style()
        style.theme_use('vista')

        actual_pos_panel = ttk.LabelFrame(self.frame, text="Actual position")
        actual_pos_panel.grid(row = 0, column = 0, sticky = 'NWSE',
        padx = (5,2.5), pady = (5,2.5))

        pin_layout = ttk.LabelFrame(self.frame, text="Pin layout")
        pin_layout.grid(row = 0, column = 1, sticky = 'NWSE',
        padx = (2.5,5), pady = (5,2.5))

        send_to_pos_panel = ttk.LabelFrame(self.frame, text="Send to position")
        send_to_pos_panel.grid(row = 1, column = 0, sticky = 'NWSE',
        padx = (5,2.5), pady = (2.5,5))

        jog_panel = ttk.LabelFrame(self.frame, text="Jog arms")
        jog_panel.grid(row = 1, column = 1, sticky = 'NWSE',
        padx = (2.5,5), pady = (2.5,5))


        # First grid
        actual_pos_panel.grid()

        axis_1_label = ttk.Label(actual_pos_panel, text="Motor 1",
        font=(self.fs, self.fsize), anchor="w")
        axis_1_label.grid(row = 0, column = 0, sticky = 'WE', padx=(0,10), pady=(0,5))
        axis_2_label = ttk.Label(actual_pos_panel, text="Motor 2",
        font=(self.fs, self.fsize), anchor="w")
        axis_2_label.grid(row = 1, column = 0, sticky = 'WE', padx=(0,10), pady=(5,5))
        axis_3_label = ttk.Label(actual_pos_panel, text="Motor 3",
        font=(self.fs, self.fsize), anchor="w")
        axis_3_label.grid(row = 2, column = 0, sticky = 'WE', padx=(0,10), pady=(5,0))

        self.axis_1_entry = ttk.Entry(actual_pos_panel, width=8, justify="right",
        font=(self.fs, self.fsize))
        self.axis_1_entry.insert("0", "{0:+.2f}".format(self.abs_pos[0])) # default érték
        self.axis_1_entry.config(state= 'disabled')
        self.axis_1_entry.grid(row = 0, column = 1, pady=(0,5))

        self.axis_2_entry = ttk.Entry(actual_pos_panel, width=8, justify="right",
        font=(self.fs, self.fsize))
        self.axis_2_entry.insert("0", "{0:+.2f}".format(self.abs_pos[1])) # default érték
        self.axis_2_entry.config(state= 'disabled')
        self.axis_2_entry.grid(row = 1, column = 1, sticky = 'WE', pady=(5,5))

        self.axis_3_entry = ttk.Entry(actual_pos_panel, width=8, justify="right",
        font=(self.fs, self.fsize))
        self.axis_3_entry.insert("0", "{0:+.2f}".format(self.abs_pos[2])) # default érték
        self.axis_3_entry.config(state= 'disabled')
        self.axis_3_entry.grid(row = 2, column = 1, sticky = 'WE', pady=(5,0))

        axis_1_unit_label = ttk.Label(actual_pos_panel, text="fok",
        anchor="w", font=(self.fs, self.fsize))
        axis_1_unit_label.grid(row = 0, column = 2, sticky = 'WE',
        padx=(5,0), pady=(0,5))
        axis_2_unit_label = ttk.Label(actual_pos_panel, text="fok",
        anchor="w", font=(self.fs, self.fsize))
        axis_2_unit_label.grid(row = 1, column = 2, sticky = 'WE',
        padx=(5,0), pady=(5,5))
        axis_3_unit_label = ttk.Label(actual_pos_panel, text="fok",
        anchor="w", font=(self.fs, self.fsize))
        axis_3_unit_label.grid(row = 2, column = 2, sticky = 'WE',
        padx=(5,0), pady=(5,0))


        # Second grid
        send_to_pos_panel.grid()

        axis_1_label_stp = ttk.Label(send_to_pos_panel, text="Motor 1",
        font=(self.fs, self.fsize), anchor="w")
        axis_1_label_stp.grid(row = 0, column = 0, sticky = 'WE', padx=(0,10), pady=(0,5))
        axis_2_label_stp = ttk.Label(send_to_pos_panel, text="Motor 2",
        font=(self.fs, self.fsize), anchor="w")
        axis_2_label_stp.grid(row = 1, column = 0, sticky = 'WE', padx=(0,10), pady=(5,5))
        axis_3_label_stp = ttk.Label(send_to_pos_panel, text="Motor 3",
        font=(self.fs, self.fsize), anchor="w")
        axis_3_label_stp.grid(row = 2, column = 0, sticky = 'WE', padx=(0,10), pady=(5,5))

        self.axis_1_entry_stp = ttk.Entry(send_to_pos_panel, width=8, justify="right",
        font=(self.fs, self.fsize))
        self.axis_1_entry_stp.insert("0", "0") # default érték
        # axis_1_entry_stp.config(state= 'disabled')
        self.axis_1_entry_stp.grid(row = 0, column = 1, pady=(0,5))

        self.axis_2_entry_stp = ttk.Entry(send_to_pos_panel, width=8, justify="right",
        font=(self.fs, self.fsize))
        self.axis_2_entry_stp.insert("0", "0")
        # axis_2_entry_stp.config(state= 'disabled')
        self.axis_2_entry_stp.grid(row = 1, column = 1, sticky = 'WE', pady=(5,5))

        self.axis_3_entry_stp = ttk.Entry(send_to_pos_panel, width=8, justify="right",
        font=(self.fs, self.fsize))
        self.axis_3_entry_stp.insert("0", "0")
        # axis_3_entry_stp.config(state= 'disabled')
        self.axis_3_entry_stp.grid(row = 2, column = 1, sticky = 'WE', pady=(5,5))

        axis_1_unit_label_stp = ttk.Label(send_to_pos_panel, text="fok",
        anchor="w", font=(self.fs, self.fsize))
        axis_1_unit_label_stp.grid(row = 0, column = 2, sticky = 'WE',
        padx=(5,0), pady=(0,5))
        axis_2_unit_label_stp = ttk.Label(send_to_pos_panel, text="fok",
        anchor="w", font=(self.fs, self.fsize))
        axis_2_unit_label_stp.grid(row = 1, column = 2, sticky = 'WE',
        padx=(5,0), pady=(5,5))
        axis_3_unit_label_stp = ttk.Label(send_to_pos_panel, text="fok",
        anchor="w", font=(self.fs, self.fsize))
        axis_3_unit_label_stp.grid(row = 2, column = 2, sticky = 'WE',
        padx=(5,0), pady=(5,5))

        send_to_position = tk.Button(send_to_pos_panel, text="GO",
        font=(self.fs, self.fsize), command=self.send_to_position)
        send_to_position.grid(row=3, columnspan=3, sticky = "WE", pady=(5,0))





    def update_abs_pos(self):

        self.abs_pos = RC.get_actual_abs_position()
        self.axis_1_entry.config(state= 'normal')
        self.axis_1_entry.delete("0", "end")
        self.axis_1_entry.insert("0", "{0:+.2f}".format(self.abs_pos[0])) # default érték
        self.axis_1_entry.config(state= 'disabled')

        self.axis_2_entry.config(state= 'normal')
        self.axis_2_entry.delete("0", "end")
        self.axis_2_entry.insert("0", "{0:+.2f}".format(self.abs_pos[1])) # default érték
        self.axis_2_entry.config(state= 'disabled')

        self.axis_3_entry.config(state= 'normal')
        self.axis_3_entry.delete("0", "end")
        self.axis_3_entry.insert("0", "{0:+.2f}".format(self.abs_pos[2])) # default érték
        self.axis_3_entry.config(state= 'disabled')


    def send_to_position(self):
        """ Convert user input to degree values to go. """

        try:
            g1 = float(self.axis_1_entry_stp.get())
            g2 = float(self.axis_2_entry_stp.get())
            g3 = float(self.axis_3_entry_stp.get())

            self.secondary_thread = threading.Thread(target=RC.move_absolute(),
            args=([g1, g2, g3]))
            self.secondary_thread.start()

            # RC.move_absolute([g1, g2, g3])
            self.update_abs_pos()

        except:
            print("User input error!")


    def func():
        """ Func. """
        pass


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

    print("Program exit!")
    sys.exit()
