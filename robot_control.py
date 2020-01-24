# -*- coding: utf-8 -*-#
import stepper_mot_control as smc
import math as m

motor_step = [4144, 4144]
resolution = [float(4144/360), float(4144/360)]
base_frequency = 500 #Hz
time_unit = float((1/base_frequency)/2)
actual_position = [0, 0] #step megadva

def move(deg1, deg2): #Megadott szogertekekhez mozgas
    step = []
    step.append(deg_to_pos(1,deg1))
    step.append(deg_to_pos(2,deg2))


    #Calc_timetable
    timetable = []
    max_step = max(abs(step[0]), abs(step[1]))

    for m in range(1,2):
        act_time = 0
        act_step = time_unit * int(max_step / step[m-1])

        for n in range(0, step[m-1]):
            act_time += act_step
            timetable.append([act_time, m, 1])
            act_time += act_step
            timetable.append([act_time, m, 0])

    time_diff_set 





    #Set dir
    if step[0] < 0: #Motor 1 iranybeallitas
        smc.dir_set(1,0)
    else:
        smc.dir_set(1,1)

    if step[1] < 0: #Motor 2 iranybeallitas
        smc.dir_set(2,0)
    else:
        smc.dir_set(2,1)


    #Set enable
    if step[0] == 0: #Motor 1 iranybeallitas
        smc.enable_set(1,1)
    else:
        smc.enable_set(1,0)

    if step[1] == 0: #Motor 2 iranybeallitas
        smc.enable_set(2,1)
    else:
        smc.enable_set(2,0)


    #Iteracio
    pass


def deg_to_pos(mot, deg):
    step = int(resolution[mot-1] * deg)
    return step



def reset_pos():
    pass


def zeroing():
    pass


try:
    while True:
        pass

except:
    pass

finally:
    pass
