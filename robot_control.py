# -*- coding: utf-8 -*-#

""" Demo robot control program.

    * App(class) -
        * init_window -
        * create -


---- Libs ----

---- Help ----

---- Info ----
C3D Kft. - Minden jog fenntartva a birtoklásra, felhasználásra,
sokszorosításra, szerkesztésre, értékesítésre nézve, valamint az ipari
tulajdonjog hatálya alá eső felhasználások esetén is.
www.C3D.hu
"""

import stepper_mot_control as smc
import math as m


""" Alap konfig. adatok a motorokra vonatkozóan:
A motor 200 impuluzusra forog egy teljes fordulatot.
A motor áttétele: 5,18.
Egy fordulat full-stepen 200 * 5,18 = 1036 inkrement.

A meglévő boardon a quarterstep (4144) és a
sixteenth step (16576) beállítások
között lehet váltani.
"""

## Hardver parameters
motor_step = [4144, 4144, 4144]
resolution = list(map(lambda x: float(float(x)/float(360)), motor_step))
step_unit = list(map(lambda x: float(1/x), resolution))
print("Stepper motor resulotion set to {0:.2f} step/deg.".format(resolution[0]))

## Running parameters
base_frequency = 5000 # Hz
correction = 0 # ms
time_unit = float(float(1/float(base_frequency)/2) - correction) # ms
print("Base frequency set to {0:.0f} Hz / {1:.5f} ms.".format(base_frequency,
time_unit))

## Actual position
actual_abs_position = [None, None, None] # abszolút szög-értékek megadva
dir = [0,0,0] # motor dir setting
jogging = False # jogging flag


def deg_to_step(deg):
    """ Háromelemű relatív szögelmozdulás-tömbből számol
    relatív lépésszámot!
    """

    step = []
    for k in range(0,len(deg)):
        step.append(m.floor(resolution[k] * deg[k]))
    return step


def check_limits():
    # TODO: write function to check movement limits
    pass


def move_absolute(deg_to_move):

    global actual_abs_position

    for k in range(0, len(deg_to_move)):
        deg_to_move[k] = deg_to_move[k] - actual_abs_position[k]

    move_relative(deg_to_move)


def sorting_steps(step):
    """ Motoronkénti lépésszám abszolútértékeinek csökkenő sorrendbe rendezése
    és a hozzá tartozó motortengely index kiszámítása. """

    abs_steps = [] # Tuple list
    sorted_steps = []
    mot = []

    # step értékek abszolútértékének betöltése, és a motor index hozzárendelése
    for m in range(0,len(step)):
        abs_steps.append( (abs(step[m]), m) )

    abs_steps.sort(reverse = True)

    print("Sorted steps acc. to motor axes: {0}".format(abs_steps))

    for ss in range(0,len(abs_steps)):
        sorted_steps.append(abs_steps[ss][0])
        mot.append(abs_steps[ss][1])

    return sorted_steps, mot


def move_relative(deg_to_move):
    """ Megadott relatív szögelfordulás-tömbhöz tartozó mozgásfüggvény.
    A mozgásfüggvény a különböző tengelyek menti lépéseket olyan sorrendben
    generálja, hogy a mozgás az összes tengelyen egyszerre fejeződik be.
    """

    steps = deg_to_step(deg_to_move)

    print("Steps to move: {0}".format(steps))
    motor_dir_set(steps) # Motorok iránybeállítása

    sort_steps = [] # A, B, ... tengelyeken lelépendő lépések
    mot_idx = [] # Az A, B, ... tengelyek indexei (0, 1, ...)

    # Step lista rendezése a hozzárendelt motor indexekkel
    sort_steps, mot_idx = sorting_steps(steps)

    motor_enable_set(1) # Motorok engedélyezése
    generate_steps(sort_steps, mot_idx) # Lépések generálása
    motor_enable_set(0) # Motorok engedélyezése

    # Update absolute position by the relative movement
    print(actual_abs_position)


def generate_steps(sorted_steps, mot_index):
    """ N-tengelyes interpoláció. Ez a függvény egy tetszőleges hosszúságú,
    csökkenő step listából és a hozzá rendelt motortengely-index listából olyan
    szekvenciát generál, amelyben az összes tengelyen egyszerre fejeződik be.
    """

    global time_unit

    size = len(sorted_steps) # Number of axes
    actual_relative_steps = []
    fi = []

    for t in range(0, size):
        actual_relative_steps.append(0)
        fi.append(0)


    ## Nested function definition BEGIN
    def check_diff(d):

        if (d >= (size-1)):
            return

        if (fi[d] < 0):
            actual_relative_steps[d+1] += 1
            # smc.onestep_mot(mot_index[d+1], time_unit)
            abs_pos_one_step(mot_index[d+1])
            # print("Step with axis: {0} ({1})".format(mot_index[d+1], actual_relative_steps[d+1]))

            fi[d] += sorted_steps[d]
            fi[d+1] -= sorted_steps[d+2]

            # Recursion with nested function
            check_diff(d+1)

    ## Nested function definition END

    # Overflow miatt hozzáadok egy nulla értékű elemet
    sorted_steps.append(0)

    while (actual_relative_steps[0] < sorted_steps[0]):
        # Initial step
        actual_relative_steps[0] += 1
        # smc.onestep_mot(mot_index[0], time_unit)
        abs_pos_one_step(mot_index[0])
        # print("Step with axis: {0} ({1})".format(mot_index[0], actual_relative_steps[0]))
        fi[0] -= sorted_steps[1]
        check_diff(0)

    # Overflow miatt hozzáadott nulla értékű elemet elveszem
    sorted_steps = sorted_steps[:-1]

    # Aktuálisan lelépett stepek
    print("Actual steps made: {0}".format(actual_relative_steps))



def jog(mot, direction):
    global jogging, dir, time_unit

    jog_time_unit = 10 * time_unit

    smc.dir_set(mot, direction)
    dir[mot] = direction

    while jogging == True:
        print("Jogging...")
        smc.onestep_mot(mot, jog_time_unit)
        abs_pos_one_step(mot)


def abs_pos_one_step(mot):
    """ Lépteti az abszolút pozíció számlálót minden egyes lépésnél
    a megfelelő irányba. """


    global actual_abs_position, dir

    if dir[mot] == 0:
        actual_abs_position[mot] -= step_unit[mot]
    else:
        actual_abs_position[mot] += step_unit[mot]



def motor_dir_set(mot_step):
    """ Háromelemű tömbnek megfelelően beállítja
    a motorok forgásirányát. """

    for d in range(0, len(mot_step)):
        if mot_step[d] < 0:
            smc.dir_set(d, 0)
            dir[d] = 0
        else:
            smc.dir_set(d, 1)
            dir[d] = 1


def motor_enable_set(enable):
    """ Engedélyezi (1) vagy letiltja (0) a motorokat. """

    # Motor 1-3 engedélyezése
    if enable == 1:
        for s in range(0,3):
            smc.enable_set(s, 1)

    # Motor 1-3 letiltás
    else:
        for s in range(0,3):
            smc.enable_set(s, 0)


def reset_pos():
    """ Abszolút szög-értékben kifejezett pozíciók nullázása. """

    global actual_abs_position
    actual_abs_position = [0,0,0]


def get_actual_abs_position():
    # global actual_abs_position
    return actual_abs_position


def zeroing(): # Always the first function to call!
    # smc.init()
    reset_pos()


# Főprogram
if __name__ == "__main__":

    zeroing()

    try:
        # smc.init()

        goal = [10,-15,12]
        goal2 = [22, -35, 25]
        move_relative(goal)
        print(goal)
        print(actual_abs_position)

        move_absolute(goal2)
        print(goal2)
        print(actual_abs_position)

        print(actual_abs_position)


    finally:
        # smc.cleanup()
        pass
