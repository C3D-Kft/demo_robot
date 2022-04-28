# -*- coding: utf-8 -*-#

""" Demo robot control program.

---- Info ----
C3D Kft. - Minden jog fenntartva a birtoklásra, felhasználásra,
sokszorosításra, szerkesztésre, értékesítésre nézve, valamint az ipari
tulajdonjog hatálya alá eső felhasználások esetén is.
www.C3D.hu
"""

# First import should be the logging module if any!
import logging
log = logging.getLogger("Main")

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

## Gripper parameters
grip_step_per_rev = 64

## Motor parameters
step_per_rev_wo_gb = 200
gear_ratio = 5.18
step_per_rev_gb = 1036.36

# 4145.45 /x4
# 16581.81 /x16
# 132 654.54 /x128

motor_step = [16582, 16582, 16582]
resolution = list(map(lambda x: float(float(x)/float(360)), motor_step))
step_unit = list(map(lambda x: float(1/x), resolution))
log.info("Stepper motor resulotion set to {0:.2f} step/deg.".format(resolution[0]))

## Running parameters
base_frequency = 2500 # Hz
correction = 0 # ms
time_unit = float(float(1/float(base_frequency)/2) - correction) # ms
log.info("Base frequency set to {0:.0f} Hz / {1:.5f} ms.".format(base_frequency,
time_unit))

## Actual position
actual_abs_position = [None, None, None] # abszolút szög-értékek megadva
dir = [0,0,0] # motor dir setting
jogging = False # jogging flag

## Axis limits default values
axis_limits_min = [-90.0, -130.0, 0.0]
axis_limits_max = [90.0, 0.0, 200.0]

## Interpolation mode
MOD = "MOD1"


def deg_to_step(deg):
    """ Háromelemű relatív szögelmozdulás-tömbből számol
    relatív lépésszámot!
    """

    step = []
    for k in range(0,len(deg)):
        step.append(m.floor(resolution[k] * deg[k]))
    return step


def check_limits(mot, pos, dir):
    """Checks if actual position is within axis limits. """

    global axis_limits_min, axis_limits_max

    if dir == 0:
        if actual_abs_position[mot] >= axis_limits_min[mot]:
            return True
        else:
            log.info("Motor{0} min. limit reached at {1}°".format(mot+1,
            axis_limits_min[mot]))
            return False

    if dir == 1:
        if actual_abs_position[mot] <= axis_limits_max[mot]:
            return True
        else:
            log.info("Motor{0} max. limit reached at {1}°".format(mot+1,
            axis_limits_max[mot]))
            return False


def move_absolute(deg_to_move):
    """ Abszolút koordináta tömbhöz tartozó mozgás. """

    global actual_abs_position

    # Check if intended pos is outside or inside limits
    for m in range(0, len(deg_to_move)):
        if deg_to_move[m] >= axis_limits_min[m]:
            if deg_to_move[m] <= axis_limits_max[m]:
                pass

            else:
                log.info("Motor{0} max. limit reached at {1}°".format(m+1,
                axis_limits_max[m]))
                return

        else:
            log.info("Motor{0} min. limit reached at {1}°".format(m+1,
            axis_limits_min[m]))
            return

    log.info("Moving to: {0}".format(deg_to_move))

    # Calculate relative movement from absolute coords.
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

    log.info("Sorted steps acc. to motor axes: {0}".format(abs_steps))

    for ss in range(0,len(abs_steps)):
        sorted_steps.append(abs_steps[ss][0])
        mot.append(abs_steps[ss][1])

    return sorted_steps, mot


def move_relative(deg_to_move):
    """ Megadott relatív szögelfordulás-tömbhöz tartozó mozgásfüggvény.
    A mozgásfüggvény a különböző tengelyek menti lépéseket olyan sorrendben
    generálja, hogy a mozgás az összes tengelyen egyszerre fejeződik be.
    """

    global MOD

    steps = deg_to_step(deg_to_move)

    log.info("Steps to move: {0}".format(steps))
    motor_dir_set(steps) # Motorok iránybeállítása

    sort_steps = [] # A, B, ... tengelyeken lelépendő lépések
    mot_idx = [] # Az A, B, ... tengelyek indexei (0, 1, ...)

    # Step lista rendezése a hozzárendelt motor indexekkel
    sort_steps, mot_idx = sorting_steps(steps)

    if MOD == "MOD1":
        generate_steps(sort_steps, mot_idx) # Lépések generálása

    else:
        generate_steps2(sort_steps, mot_idx) # Lépések generálása


    # Update absolute position by the relative movement
    log.info("Actual position: [{0:.3f}, {1:.3f}, {2:.3f}]".format(
    actual_abs_position[0], actual_abs_position[1], actual_abs_position[2]))


def generate_steps2(sorted_steps, mot_index):

    global time_unit

    for m in range(0, len(mot_index)): # 0, 1, 2

        for s in range(0, sorted_steps[m]):
            smc.onestep_mot(mot_index[m], time_unit)
            abs_pos_one_step(mot_index[m])



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


    """ Nested function definition BEGIN """
    def check_diff(d):

        if (d >= (size-1)):
            return

        if (fi[d] < 0):
            actual_relative_steps[d+1] += 1
            smc.onestep_mot(mot_index[d+1], time_unit)
            abs_pos_one_step(mot_index[d+1])
            # print("Step with axis: {0} ({1})".format(mot_index[d+1],
            # actual_relative_steps[d+1]))

            fi[d] += sorted_steps[d]
            fi[d+1] -= sorted_steps[d+2]

            # Recursion with nested function
            check_diff(d+1)

    """ Nested function definition END """

    # Overflow miatt hozzáadok egy nulla értékű elemet
    sorted_steps.append(0)

    while (actual_relative_steps[0] < sorted_steps[0]):
        # Initial step
        actual_relative_steps[0] += 1
        smc.onestep_mot(mot_index[0], time_unit)
        abs_pos_one_step(mot_index[0])
        # print("Step with axis: {0} ({1})".format(mot_index[0],
        # actual_relative_steps[0]))
        fi[0] -= sorted_steps[1]
        check_diff(0)

    # Overflow miatt hozzáadott nulla értékű elemet elveszem
    sorted_steps = sorted_steps[:-1]

    # Aktuálisan lelépett stepek
    log.info("Actual steps made: {0}".format(actual_relative_steps))



def jog(mot, direction):
    """ This function enables to jog motors/axes individually. The motor
    jog until the jogging flag - which is set from a parallel thread - is
    True. """

    global jogging, dir, time_unit

    # TODO: visszakorrigálni, ha kész a tesztelés
    jog_time_unit = 1 * time_unit

    # Precheck if motor is at limits or not
    if check_limits(mot, actual_abs_position[mot], direction) == False:
        return

    msg = smc.dir_set(mot, direction)
    log.info(msg)
    dir[mot] = direction

    log.info("Jogging...")

    while jogging == True:
        # Check if limit is reached
        if check_limits(mot, actual_abs_position[mot], direction) == False:
            break
        else:
            smc.onestep_mot(mot, jog_time_unit) # Step one

        abs_pos_one_step(mot) # Update pos.

    log.info("Jogging stopped!")


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
            msg = smc.dir_set(d, 0)
            log.info(msg)
            dir[d] = 0
        else:
            msg = smc.dir_set(d, 1)
            log.info(msg)
            dir[d] = 1


def motor_enable_set(enable):
    """ Engedélyezi (1) vagy letiltja (0) a motorokat. """

    # Motor 1-3 letiltás
    if enable == 1:
        for s in range(0,3):
            msg = smc.enable_set(s, 1)
            log.info(msg)

    # Motor 1-3 engedélyezése
    if enable == 0:
        for s in range(0,3):
            msg = smc.enable_set(s, 0)
            log.info(msg)


def reset_pos():
    """ Abszolút szög-értékben kifejezett pozíciók nullázása. """

    global actual_abs_position
    actual_abs_position = [0,0,0]


def get_actual_abs_position():
    """ Get actual absolute position. """

    return actual_abs_position


def get_limits():
    """ Get axis limits lists. """

    global axis_limits_min, axis_limits_max

    return axis_limits_min, axis_limits_max


def set_limits(limits_min, limits_max):
    """ Set axis limits lists. """

    global axis_limits_min, axis_limits_max

    axis_limits_min = limits_min
    axis_limits_max = limits_max
    log.info("Limits has been set!")


def grip_release():
    """ Turn gripper motor half revolution to force open the gripper
    arms against the spring.
    """

    # for m in range(0,32):
    smc.step_gripper(1)
    # print("Step: {0}".format(m))


def grip_hold():
    """ Turn gripper motor half revolution to let the springs close the gripper
    arms.
    """

    #for m in range(0,32):
    smc.step_gripper(0)
    # print("Step: {0}".format(m))


def init(): # Always the first function to call!
    """ First function to call. This func. initializes the GPIO outputs. """

    smc.init()
    log.info("Robot initialized!")


def poweron():
    log.info("Power switched on!")
    smc.poweron()


def poweroff():
    log.info("Power switched off!")
    smc.poweroff()


def switch_mode(mode):
    global MOD
    MOD = mode


def zeroing():
    """ ... """
    reset_pos()


def cleanup():
    """ Last function to call. This func. cleanup the GPIO outputs. """

    log.info("Robot GPIOs cleaned up!")
    smc.cleanup()



# Főprogram
if __name__ == "__main__":

    zeroing()

    try:
        init()

        goal = [10,0,0]
        goal2 = [20,0,0]

        # Test relative movement
        move_relative(goal)
        print(goal)
        print(actual_abs_position)

        # Test absolute movement
        move_absolute(goal2)
        print(goal2)
        print(actual_abs_position)

    finally:
        cleanup()
