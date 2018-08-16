#  Copyright 2018 Alvaro Villoslada (Alvipe)
#  This file is part of Open Myo.
#  Open Myo is distributed under a GPL 3.0 license

import open_myo2 as myo
import numpy as np
import timeit
import time
import pickle

get_reading = False

primeira = 0

posi = "Fechada"
quem = "Gio"
data = "_13_08_2018"
pasta = "coletaRAW/"
tipo = "_RAW_"
quant_amostras = 5

nome_arquivo = pasta + quem + data + tipo + posi + ".npz"

quant_vezes = 10
contagem = 0

def process_emg(emg):
    if get_reading:
        emg0 = emg[0:8]
        emg1 = emg[8:16]

        global primeira, contagem

        if primeira == 0:
            primeira = 1
            global amostra
            amostra = np.array([emg0])
            amostra = np.append(amostra, np.array([emg1]), axis=0)
            # Salva as outras amostras da sequência
        else:
            amostra = np.append(amostra, np.array([emg0]), axis=0)
            amostra = np.append(amostra, np.array([emg1]), axis=0)
        #print(amostra)
       



def save_data(amostra):
    
    # Abre o arquivo da posição requerida. Caso não exista, cria este arquivo
    try:
        npzfile = np.load(nome_arquivo)
        datax = np.append(npzfile['x'], amostra, axis=0)
        np.savez(nome_arquivo, x=datax)
    except IOError:
        np.savez(nome_arquivo, x=amostra)
    npzfile = np.load(nome_arquivo)
    print("Foram adicionadas %d coletas" % ((quant_amostras * (contagem - 1)) * 2))
    print("Coletas Acumuladas: " + str(len(npzfile['x'])))


myo_device = myo.Device()
myo_device.services.sleep_mode(1) # never sleep
myo_device.services.set_leds([0, 0, 255], [0, 0, 255])  # purple logo and bar LEDs)
myo_device.services.vibrate(1) # short vibration
# myo_device.services.emg_filt_notifications()
myo_device.services.emg_raw_notifications()
myo_device.services.set_mode(myo.EmgMode.RAW, myo.ImuMode.OFF, myo.ClassifierMode.OFF)
#myo_device.services.set_mode(myo.EmgMode.OFF, myo.ImuMode.OFF, myo.ClassifierMode.OFF)
time.sleep(1)
myo_device.add_emg_event_handler(process_emg)


runtime = 1

for j in range(quant_vezes):
    contagem += 1
    input("Pressione para a contagem %d" % contagem)
    myo_device.services.vibrate(1) # short vibration
    for i in range(quant_amostras):
        #print("i: " + str(i))
        #time.sleep(2)

        start_time = timeit.default_timer()
        tick = start_time
        get_reading = True
        while round(tick - start_time, 1) <= runtime:
            if myo_device.services.waitForNotifications(1):
                tick = timeit.default_timer()
    #               continue
            else:
                print("Waiting...")

        
        get_reading = False
        
        #time.sleep(2)
    myo_device.services.vibrate(1) # short vibration
    print("Fim da coleta %d" % (contagem))
    print()

save_data(amostra)
print(tick - start_time)   
