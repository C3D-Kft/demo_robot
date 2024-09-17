# -*- coding: utf-8 -*-#
# !/usr/bin/python3

""" Demo robot control program.

---- Info ----
C3D Kft. - Minden jog fenntartva a birtoklásra, felhasználásra,
sokszorosításra, szerkesztésre, értékesítésre nézve, valamint az ipari
tulajdonjog hatálya alá eső felhasználások esetén is.
www.C3D.hu

---- Alapadatok ----
Alap konfig. adatok a motorokra vonatkozóan:
A motor 200 impuluzusra forog egy teljes fordulatot.
A motor áttétele: 5,18.
Egy fordulat full-stepen 200 * 5,18 = 1036 inkrement.

A meglévő boardon a quarterstep (4144) és a
sixteenth step (16576) beállítások
között lehet váltani.

"""

from enum import Enum
import logging
import math as m
import stepper_mot_control as smc

log = logging.getLogger("Main")

# Gripper parameters
GRIP_STEP_PER_REV = 64

# Motor parameters
STEP_PER_REV_WO_GEARBOX = 200
GEAR_RATIO = 5.18
STEP_PER_REV_GEARBOX = 1036.36

# 1036
# 4145.45 /x4
# 8290.88 /x8
# 16581.81 /x16
# 66 327.04 /x64
# 132 654.54 /x128

motor_step = [4145.45, 4145.45, 4145.45]
resolution = list(map(lambda x: float(float(x)/float(360)), motor_step))
step_unit = list(map(lambda x: float(1/x), resolution))
log.info("Stepper motor resolution set to {resolution[0]:.2f} step/deg.")

# Running parameters
BASE_FREQUENCY = 750  # Hz
CORRECTION = 0  # ms
TIME_UNIT = float(float(1/float(BASE_FREQUENCY)/2) - CORRECTION)  # ms
log.info(f"Base frequency set to {BASE_FREQUENCY:.0f} Hz / {TIME_UNIT:.5f} ms.")

# Actual position
ACTUAL_ABS_POSITION = [0, 0, 0]  # abszolút szög-értékek megadva
DIRECTION = [0, 0, 0]  # motor dir setting
JOGGING = False  # jogging flag

# Axis limits default values
AXIS_LIMITS_MIN = [-90.0, -130.0, 0.0]
AXIS_LIMITS_MAX = [90.0, 0.0, 200.0]


class Interpolation(Enum):
    MOD1 = 1  # Interpolation - all axis reach end simultaneously
    MOD2 = 2  # No interpolation between motor axes


# Interpolation mode
MOD = Interpolation.MOD1


def deg_to_step(deg):
    """ Háromelemű relatív szögelmozdulás-tömbből számol
    relatív lépésszámot!
    """
    step = []
    for idx, val in enumerate(deg):
        step.append(m.floor(resolution[idx] * val))
    return step


def check_limits(mot, direction):
    """Checks if actual position is within axis limits (for jogging). """
    if direction == 0:
        if ACTUAL_ABS_POSITION[mot] >= AXIS_LIMITS_MIN[mot]:
            return True

        log.info(
            "Motor%s min. limit reached at %s°", mot+1,
            AXIS_LIMITS_MIN[mot]
        )
        return False

    if direction == 1:
        if ACTUAL_ABS_POSITION[mot] <= AXIS_LIMITS_MAX[mot]:
            return True

        log.info(
            "Motor%s max. limit reached at %s°", mot+1,
            AXIS_LIMITS_MAX[mot]
        )
        return False

    return False


def move_absolute(deg_to_move):
    """ Abszolút koordináta tömbhöz tartozó mozgás. """

    # Check if intended pos is outside or inside limits
    for mot, deg in enumerate(deg_to_move):
        if deg >= AXIS_LIMITS_MIN[mot]:
            if deg <= AXIS_LIMITS_MAX[mot]:
                pass

            else:
                log.info(
                    "Motor%s max. limit reached at %s°", mot+1,
                    AXIS_LIMITS_MAX[mot]
                )
                return

        else:
            log.info(
                "Motor%s min. limit reached at %s°", mot+1,
                AXIS_LIMITS_MIN[mot]
            )
            return

    log.info("Moving to: %s", deg_to_move)

    # Calculate relative movement from absolute coords.
    for idx, val in enumerate(deg_to_move):
        deg_to_move[idx] = val - ACTUAL_ABS_POSITION[idx]

    move_relative(deg_to_move)


def move_absolute_loop(deg_to_move):
    """ Abszolút koordináta tömbhöz tartozó mozgás. """

    def sign(x):
        """ Signum function, return 1, -1 or 0; depending on the sign. """
        if x > 0:
            return 1
        elif x < 0:
            return -1
        else:
            return 0

    # Check if intended pos is outside or inside limits
    # Move this check to parent function, to check all datapoints before running

    asp = [0, 0, 0]  # Current position in absolute steps (from start pos.)
    step_list = []  # List with relative step arrays
    direction = []  # Init direction with first deg. values
    for deg in deg_to_move[0]:
        direction.append(sign(deg))

    n = 0

    # Calculate relative step array for the movement loop
    # First element excluded as it is the start point
    for deg in deg_to_move[:-1]:
        n += 1
        # Calculate absolute steps from absolute degrees (target-start deg.)
        step0, step1, step2 = deg_to_step([
            deg[0] - ACTUAL_ABS_POSITION[0],
            deg[1] - ACTUAL_ABS_POSITION[1],
            deg[2] - ACTUAL_ABS_POSITION[2]
        ])
        # Difference between actual pos. and previous pos.
        dsp = [step0 - asp[0], step1 - asp[1], step2 - asp[2]]

        # If all relative steps are zero, skip this calculation
        if dsp[0] == 0 and dsp[1] == 0 and dsp[2] == 0:
            continue

        # Check if steps changing direction, and set flag
        if ((sign(dsp[0]) == direction[0] or dsp[0] == 0) and
                (sign(dsp[1]) == direction[1] or dsp[1] == 0) and
                (sign(dsp[2]) == direction[2] or dsp[2] == 0)):
            step_list.append([dsp[0], dsp[1], dsp[2], None])  # No change

        else:
            # Direction changed
            direction = [sign(dsp[0]), sign(dsp[1]), sign(dsp[2])]
            step_list.append([dsp[0], dsp[1], dsp[2], direction])

        # Save values for next iteration
        asp = [step0, step1, step2]
        print(step_list[-1])

    # Set motor direction before start
    motor_dir_set(step_list[0][:-1])

    # Generating movement, iterating over the full relative step list
    n = 0
    for steps in step_list:
        n += 1
        # If direction flag 1 (changed), set motor directions
        if steps[3] is not None:
            motor_dir_set(steps[3])

        # Move each axis one-by-one
        for mot in [0, 1, 2]:
            for _ in range(0, abs(steps[mot])):
                smc.onestep_mot(mot, TIME_UNIT)
                abs_pos_one_step(mot)


def sorting_steps(step):
    """ Motoronkénti lépésszám abszolútértékeinek csökkenő sorrendbe rendezése
    és a hozzá tartozó motortengely index kiszámítása.
    """
    abs_steps = []  # Tuple list
    sorted_steps = []
    mot = []

    # step értékek abszolútértékének betöltése, és a motor index hozzárendelése
    for i, mot_step in enumerate(step):
        abs_steps.append((abs(mot_step), i))

    abs_steps.sort(reverse=True)

    log.info("Sorted steps acc. to motor axes: %s", abs_steps)

    for i in range(0, len(abs_steps)):
        sorted_steps.append(abs_steps[i][0])
        mot.append(abs_steps[i][1])

    return sorted_steps, mot


def move_relative(deg_to_move):
    """ Megadott relatív szögelfordulás-tömbhöz tartozó mozgásfüggvény.
    A mozgásfüggvény a különböző tengelyek menti lépéseket olyan sorrendben
    generálja, hogy a mozgás az összes tengelyen egyszerre fejeződik be.
    """
    steps = deg_to_step(deg_to_move)

    log.info("Steps to move: %s", steps)
    motor_dir_set(steps)  # Motorok iránybeállítása

    # Step lista rendezése a hozzárendelt motor indexekkel
    # sort_steps: A, B, ... tengelyeken lelépendő lépések
    # mot_idx: Az A, B, ... tengelyek indexei (0, 1, ...)
    sort_steps, mot_idx = sorting_steps(steps)

    # Lépések generálása
    if MOD == Interpolation.MOD1:
        generate_steps_by_interpolation(sort_steps, mot_idx)

    elif MOD == Interpolation.MOD2:
        generate_steps_by_axis(sort_steps, mot_idx)

    # Update absolute position by the relative movement
    log.info(
        "Actual position: [{0:.3f}, {1:.3f}, {2:.3f}]".format(
            ACTUAL_ABS_POSITION[0],
            ACTUAL_ABS_POSITION[1],
            ACTUAL_ABS_POSITION[2]
        )
    )


def generate_steps_by_axis(sorted_steps, mot_index):
    """ Tengelyenkénti lépés. Ez a függvény egy tetszőleges hosszúságú,
    step listából és a hozzá rendelt motortengely-index listából olyan
    szekvenciát generál, amelyben a tengelyenként mozgások egymás után
    következnek (nincs interpoláció).
    """
    for mot in range(0, len(mot_index)):  # 0, 1, 2
        for i in range(0, sorted_steps[mot]):
            smc.onestep_mot(mot_index[mot], TIME_UNIT)
            abs_pos_one_step(mot_index[mot])


def generate_steps_by_interpolation(sorted_steps, mot_index):
    """ N-tengelyes interpoláció. Ez a függvény egy tetszőleges hosszúságú,
    csökkenő step listából és a hozzá rendelt motortengely-index listából olyan
    szekvenciát generál, amelyben az összes tengelyen egyszerre fejeződik be a
    mozgás.
    """
    size = len(sorted_steps)  # Number of axes
    actual_relative_steps = []
    fii = []

    for i in range(0, size):
        actual_relative_steps.append(0)
        fii.append(0)

    # NOTE: Nested function definition BEGIN
    def check_diff(dif):

        if dif >= (size-1):
            return

        if fii[dif] < 0:
            actual_relative_steps[dif+1] += 1
            smc.onestep_mot(mot_index[dif+1], TIME_UNIT)
            abs_pos_one_step(mot_index[dif+1])

            fii[dif] += sorted_steps[dif]
            fii[dif+1] -= sorted_steps[dif+2]

            # Recursion with nested function
            check_diff(dif+1)

    # NOTE: Nested function definition END

    # Overflow miatt hozzáadok egy nulla értékű elemet
    sorted_steps.append(0)

    while actual_relative_steps[0] < sorted_steps[0]:
        # Initial step
        actual_relative_steps[0] += 1
        smc.onestep_mot(mot_index[0], TIME_UNIT)
        abs_pos_one_step(mot_index[0])
        fii[0] -= sorted_steps[1]
        check_diff(0)

    # Overflow miatt hozzáadott nulla értékű elemet elveszem
    sorted_steps = sorted_steps[:-1]

    # Aktuálisan lelépett stepek
    log.info("Actual steps made: %s", actual_relative_steps)


def jog(mot, direction):
    """ This function enables to jog motors/axes individually. The motor
    jog until the jogging flag - which is set from a parallel thread - is
    True.
    """
    global JOGGING

    # TODO: visszakorrigálni, ha kész a tesztelés
    jog_time_unit = 1 * TIME_UNIT

    # Precheck if motor is at limits or not
    if not check_limits(mot, direction):
        return

    msg = smc.dir_set(mot, direction)
    log.info(msg)
    DIRECTION[mot] = direction

    log.info("Jogging...")

    while JOGGING:  # While True
        # Check if limit is reached
        if not check_limits(mot, direction):
            break

        smc.onestep_mot(mot, jog_time_unit)  # Step one
        abs_pos_one_step(mot)  # Update pos.

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

    for idx, step in enumerate(mot_step):
        if step < 0:
            msg = smc.dir_set(idx, 0)
            log.info(msg)
            DIRECTION[idx] = 0
        elif step > 0:  # Korábban: else volt !!
            msg = smc.dir_set(idx, 1)
            log.info(msg)
            DIRECTION[idx] = 1


def motor_enable_set(enable):
    """ Engedélyezi (1) vagy letiltja (0) a motorokat. """

    # Motor 1-3 letiltása
    if enable == 1:
        for i in range(0, 3):
            msg = smc.enable_set(i, 1)
            log.info(msg)

    # Motor 1-3 engedélyezése
    if enable == 0:
        for i in range(0, 3):
            msg = smc.enable_set(i, 0)
            log.info(msg)


def reset_pos():
    """ Abszolút szög-értékben kifejezett pozíciók nullázása. """
    global ACTUAL_ABS_POSITION
    ACTUAL_ABS_POSITION = [0, 0, 0]


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
    smc.step_gripper(1)


def grip_hold():
    """ Turn gripper motor half revolution to let the springs close the gripper
    arms.
    """
    smc.step_gripper(0)


def init():  # Always the first function to call!
    """ First function to call. This func. initializes the GPIO outputs. """
    smc.init()
    log.info("Robot initialized!")
    poweron()


def poweron():
    """ Switch on power. """
    log.info("Power switched on!")
    smc.poweron()


def poweroff():
    """ Switch off power. """
    log.info("Power switched off!")
    smc.poweroff()


def switch_mode(mode: int):
    """ Switch operating mode back-and-forth. """
    global MOD
    MOD = mode


def zeroing():
    """ ... """
    reset_pos()


def cleanup():
    """ Last function to call. This func. cleanup the GPIO outputs. """

    log.info("Robot GPIOs cleaned up!")
    smc.cleanup()


# Include guard
if __name__ == "__main__":

    zeroing()

    try:
        init()

        goal = [10, 0, 0]
        goal2 = [20, 0, 0]

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
