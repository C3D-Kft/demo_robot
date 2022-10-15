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

import math as m
import stepper_mot_control as smc


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
# 8290.88
# 16581.81 /x16
# 66 327.04 /x64
# 132 654.54 /x128

motor_step = [8291, 8291, 8291]
resolution = list(map(lambda x: float(float(x)/float(360)), motor_step))
step_unit = list(map(lambda x: float(1/x), resolution))
log.info("Stepper motor resulotion set to {0:.2f} step/deg.".format(resolution[0]))

## Running parameters
base_frequency = 750 # Hz
correction = 0 # ms
TIME_UNIT = float(float(1/float(base_frequency)/2) - correction) # ms
log.info("Base frequency set to {0:.0f} Hz / {1:.5f} ms.".format(base_frequency,
TIME_UNIT))

## Actual position
ACTUAL_ABS_POSITION = [None, None, None] # abszolút szög-értékek megadva
DIRECTION = [0,0,0] # motor dir setting
JOGGING = False # jogging flag

## Axis limits default values
AXIS_LIMITS_MIN = [-90.0, -130.0, 0.0]
AXIS_LIMITS_MAX = [90.0, 0.0, 200.0]

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


def check_limits(mot, pos, direction):
    """Checks if actual position is within axis limits. """

    # lobal AXIS_LIMITS_MIN, AXIS_LIMITS_MAX

    if direction == 0:
        if ACTUAL_ABS_POSITION[mot] >= AXIS_LIMITS_MIN[mot]:
            return True

        log.info("Motor%s min. limit reached at %s°", mot+1,
        AXIS_LIMITS_MIN[mot])
        return False

    if direction == 1:
        if ACTUAL_ABS_POSITION[mot] <= AXIS_LIMITS_MAX[mot]:
            return True

        log.info("Motor%s max. limit reached at %s°", mot+1,
        AXIS_LIMITS_MAX[mot])
        return False


def move_absolute(deg_to_move):
    """ Abszolút koordináta tömbhöz tartozó mozgás. """

    global ACTUAL_ABS_POSITION

    # Check if intended pos is outside or inside limits
    for m in range(0, len(deg_to_move)):
        if deg_to_move[m] >= AXIS_LIMITS_MIN[m]:
            if deg_to_move[m] <= AXIS_LIMITS_MAX[m]:
                pass

            else:
                log.info("Motor{0} max. limit reached at {1}°".format(m+1,
                AXIS_LIMITS_MAX[m]))
                return

        else:
            log.info("Motor{0} min. limit reached at {1}°".format(m+1,
            AXIS_LIMITS_MIN[m]))
            return

    log.info("Moving to: {0}".format(deg_to_move))

    # Calculate relative movement from absolute coords.
    for k in range(0, len(deg_to_move)):
        deg_to_move[k] = deg_to_move[k] - ACTUAL_ABS_POSITION[k]

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
    ACTUAL_ABS_POSITION[0], ACTUAL_ABS_POSITION[1], ACTUAL_ABS_POSITION[2]))


def generate_steps2(sorted_steps, mot_index):

    global TIME_UNIT

    for m in range(0, len(mot_index)): # 0, 1, 2

        for s in range(0, sorted_steps[m]):
            smc.onestep_mot(mot_index[m], TIME_UNIT)
            abs_pos_one_step(mot_index[m])



def generate_steps(sorted_steps, mot_index):
    """ N-tengelyes interpoláció. Ez a függvény egy tetszőleges hosszúságú,
    csökkenő step listából és a hozzá rendelt motortengely-index listából olyan
    szekvenciát generál, amelyben az összes tengelyen egyszerre fejeződik be.
    """

    global TIME_UNIT

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
            smc.onestep_mot(mot_index[d+1], TIME_UNIT)
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
        smc.onestep_mot(mot_index[0], TIME_UNIT)
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

    global JOGGING, DIRECTION, TIME_UNIT

    # TODO: visszakorrigálni, ha kész a tesztelés
    jog_time_unit = 1 * TIME_UNIT

    # Precheck if motor is at limits or not
    if not check_limits(mot, ACTUAL_ABS_POSITION[mot], direction):
        return

    msg = smc.dir_set(mot, direction)
    log.info(msg)
    DIRECTION[mot] = direction

    log.info("Jogging...")

    while JOGGING: # Amíg True
        # Check if limit is reached
        if not check_limits(mot, ACTUAL_ABS_POSITION[mot], direction):
            break

        smc.onestep_mot(mot, jog_time_unit) # Step one
        abs_pos_one_step(mot) # Update pos.

    log.info("Jogging stopped!")


def abs_pos_one_step(mot):
    """ Lépteti az abszolút pozíció számlálót minden egyes lépésnél
    a megfelelő irányba. """


    global ACTUAL_ABS_POSITION

    if DIRECTION[mot] == 0:
        ACTUAL_ABS_POSITION[mot] -= step_unit[mot]
    else:
        ACTUAL_ABS_POSITION[mot] += step_unit[mot]


def motor_dir_set(mot_step):
    """ Háromelemű tömbnek megfelelően beállítja
    a motorok forgásirányát. """

    for i in range(0, len(mot_step)):
        if mot_step[i] < 0:
            msg = smc.dir_set(i, 0)
            log.info(msg)
            DIRECTION[i] = 0
        else:
            msg = smc.dir_set(i, 1)
            log.info(msg)
            DIRECTION[i] = 1


def motor_enable_set(enable):
    """ Engedélyezi (1) vagy letiltja (0) a motorokat. """

    # Motor 1-3 letiltás
    if enable == 1:
        for i in range(0,3):
            msg = smc.enable_set(i, 1)
            log.info(msg)

    # Motor 1-3 engedélyezése
    if enable == 0:
        for i in range(0,3):
            msg = smc.enable_set(i, 0)
            log.info(msg)


def reset_pos():
    """ Abszolút szög-értékben kifejezett pozíciók nullázása. """

    global ACTUAL_ABS_POSITION
    ACTUAL_ABS_POSITION = [0,0,0]


def get_actual_abs_position():
    """ Get actual absolute position. """

    return ACTUAL_ABS_POSITION


def get_limits():
    """ Get axis limits lists. """

    return AXIS_LIMITS_MIN, AXIS_LIMITS_MAX


def set_limits(limits_min, limits_max):
    """ Set axis limits lists. """

    global AXIS_LIMITS_MIN, AXIS_LIMITS_MAX

    AXIS_LIMITS_MIN = limits_min
    AXIS_LIMITS_MAX = limits_max
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
    poweron()


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
        print(ACTUAL_ABS_POSITION)

        # Test absolute movement
        move_absolute(goal2)
        print(goal2)
        print(ACTUAL_ABS_POSITION)

    finally:
        cleanup()
