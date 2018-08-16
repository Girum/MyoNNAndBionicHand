'''

    Carlos Eduardo Palmieri Teixeira & Giovanni Antunes Bonin
    Script pertencente ao Trabalho de Conclusao de Curso.
    2018.
    
    Script para obtencao de dados EMG da Myo Armband. Faz a captura de uma posicao
    individual.
    
'''
import open_myo2 as myo
from sklearn.externals import joblib
import sys
import numpy as np
import threading
import time
import timeit
import math


t = 0
primeira = 0
contagem = 1
vai = True

runtime = 1

#editavel
posi = "Aberta"
quem = "Gio"
data = "_13_08_2018"
pasta = "coletaRAW/"
tipo = "_RAW_"
quant_amostras = 160
quant_vezes = 10

#nao editavel
nome_arquivo = pasta + quem + data + tipo + posi + ".npz"

#handler responsavel por receber os dados
def process_emg(emg):

    global vai
    global t
    global contagem

    '''dados vem em um vetor de 16 por caracteristica. Divide-se em 2, para
    2 vetores de 16'''

    if vai:
        emg0 = emg[0:8]
        emg1 = emg[8:16]

        #Verifica se foram coletadas todas as quantidades de amostra discriminada em "quant_amostras"
        if t < quant_amostras:
            t += 1
            #Necessario para salvar as primeiras amostras da sequencia
            global primeira
            if primeira == 0:
                primeira = 1
                global amostra
                amostra = np.array([emg0])
                amostra = np.append(amostra, np.array([emg1]), axis=0)
            #Salva as outras amostras da sequencia
            else:
                amostra = np.append(amostra, np.array([emg0]), axis=0)
                amostra = np.append(amostra, np.array([emg1]), axis=0)
        else:
            print("Fim da coleta %d" % (contagem))
            print()
            contagem += 1
            t = 0
            #Verifica se a quantidade de vezes de coleta por programa foi atingido
            if contagem == (quant_vezes + 1):
                #Abre o arquivo da posicao requerida. Caso nao exista, cria este arquivo
                try:
                    npzfile = np.load(nome_arquivo)
                    datax = np.append(npzfile['x'], amostra, axis=0)
                    np.savez(nome_arquivo, x=datax)
                except IOError:
                    np.savez(nome_arquivo, x=amostra)
                npzfile = np.load(nome_arquivo)
                print("Foram adicionadas %d coletas" % ((quant_amostras * (contagem - 1))*2))
                print("Coletas Acumuladas: " + str(len(npzfile['x'])))
                global Fim
                Fim = False
            else:
                #Vibra para saber que sera realizada a proxima amostra
                myo_device.services.vibrate(1)
                #Apos pressionar ENTER, fara a proxima coleta (da mesma posicao)
                input("Pressione ENTER para a proxima coleta")
                vai = True
                #Impede a Myo de entrar em deep sleep, e ocasionalmente falhar a comunicacao
                myo_device.services.sleep_mode(1)
                print()
                print("Inicio da coleta: %d" % contagem)

#Captura o endereco MAC da Myo
myo_mac_addr = myo.get_myo()
print("MAC address: %s" % myo_mac_addr)

#Inicia um novo dispositivo Myo
myo_device = myo.Device()

#Previne que a pulseira entre em Sleep apos certo tempo
myo_device.services.sleep_mode(1)

#Vibra a Myo para saber que conectou
myo_device.services.vibrate(1)

#Verifica o nivel de bateria da Myo
batt = myo_device.services.battery()
print("Battery level: %d" % batt)

#Habilita as notificacoes de EMG tipo RAW
myo_device.services.emg_raw_notifications()

#Seta o modo do EMG (RAW, IMU_OFF, CLASSIFIER_OFF)
myo_device.services.set_mode(myo.EmgMode.RAW, myo.ImuMode.OFF, myo.ClassifierMode.OFF)

#Adiciona o Handler recebe_emg ao pool de handlers EMG
myo_device.add_emg_event_handler(process_emg)

#Informacoes sobre o arquivo que sera utilizado e inicio de coleta apos pressionar ENTER
print("Nome do arquivo:" + nome_arquivo)
print()
input("Pressione ENTER para iniciar a coleta")
print()
print("Inicio da coleta: 1")

#Constante do while para o programa rodar ata que mude para 0
Fim = True

start_time = timeit.default_timer()
tick = start_time

while round(tick-start_time, 1) <= runtime:
    #Verifica se ha alguma notificacao de handler
    if myo_device.services.waitForNotifications(1):
        tick = timeit.default_timer()
        #continue
    else:
        print("Waiting...")
vai = False
