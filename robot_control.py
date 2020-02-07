# -*- coding: utf-8 -*-#
import stepper_mot_control as smc
import math as m
import time

#Alap konfig adatok a motorokra vonatkozóan
motor_step = [4144, 4144, 4144]
resolution = list(map(lambda x: float(x/360), motor_step))
# resolution = [float(4144/360), float(4144/360), float(4144/360)]
base_frequency = 5000 # Hz
correction = 0 #ms
time_unit = float( float(1/float(base_frequency)/2) - correction) # ms
actual_position = [0, 0, 0] # abszolút szög-érték megadva


def deg_to_step(deg):
    """ Háromelemű relatív szög-tömbből számol relatív lépésszámot! """
    step = []
    for k in range(0,len(deg)):
        # step.append(int(resolution[k] * deg[k]))
        step.append(m.floor(resolution[k] * deg[k]))
    return step


def move(step):
    """ Megadott lépésszámokhoz (tömb) tartozó mozgásfüggvény """
    print(step)
    motor_dir_set(step) #Motorok iránybeállítása

    #3d interpolator
    # A, B, C tengelyeken lépendő lépések abszolútértéke // a3 =|dx|, b3 =|dy|, c3 =|dz|
    dp = []
    for m in range(0,len(step)):
        dp.append(abs(step[m])) #step értékek abszolútértékének betöltése a dp[] tömbbe

    fab = dp[0] - dp[1] #a3 - b3
    fac = dp[0] - dp[2] #a3 - c3
    a2 = b2 = c2 = 0 #aktuális rel pozício

    #Iteracio
    stepnum = 0 # Hányadik lépésnél tartok
    # print("Lépés, fab, fac, a2, b2, c2")
    # print("{0}. lépés: {1}, {2}, {3}, {4}, {5}".format(stepnum, fab, fac, a2, b2, c2))

    #This is where the magic happens!
    while ((a2 != dp[0]) or (b2 != dp[1]) or (c2 != dp[2])):
        stepnum += 1
        if abs(fab) >= abs(fac):
            if fab > 0:
                a2 += 1 #motor 1 léptetese
                onestep_mot(0)
                fab = fab - dp[1]
                fac = fac - dp[2]
            else:
                b2 += 1 #motor 2 leptetese
                onestep_mot(1)
                fab = fab + dp[0]
        else:
            if fac > 0:
                a2 += 1 #motor 1 léptetése
                onestep_mot(0)
                fab = fab - dp[1]
                fac = fac - dp[2]
            else:
                c2 += 1 #motor 2 leptetese
                onestep_mot(2)
                fac = fac + dp[0]

        #print("{0}. lépés: {1}, {2}, {3}, {4}, {5}".format(stepnum, fab, fac, a2, b2, c2))


def onestep_mot(mot):
    """ Adott motornak 1db négszögjel kiadása """
    smc.move(mot,1)
    time.sleep(time_unit)
    smc.move(mot, 0)
    time.sleep(time_unit)


def motor_dir_set(mot_step):
    """ Háromelemű tömbnek megfelelően beállítja
    a motorok forgásirányát """

    for d in range(0,len(mot_step)):
        if mot_step[d] < 0: #d indexű motor iranybeallitas
            smc.dir_set(d,0)
        else:
            smc.dir_set(d,1)


def motor_enable_set(enable):
    """ Engedélyezi (1) vagy letiltja (0) a motorokat """

    if enable == 1: #Motor 1-3 engedelyezes
        for s in range(0,3):
            smc.enable_set(s,1)

    else:           #Motor 1-3 letiltas
        for s in range(0,3):
            smc.enable_set(s,0)


def reset_pos():
    pass


def zeroing():
    pass

#Főprogram
if __name__ == "__main__":
    motor_enable_set(1)
    move(deg_to_step([180,-180,180]))
    motor_enable_set(0)
    smc.cleanup()

    # try:
    #     motor_enable_set(1)
    #     move(deg_to_pos([25,30,45]))
    #
    # except:
    #     pass
    #
    # finally:
    #     motor_enable_set(0)
