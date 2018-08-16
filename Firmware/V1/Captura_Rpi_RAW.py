'''

    Carlos Eduardo Palmieri Teixeira & Giovanni Antunes Bonin
    Script pertencente ao Trabalho de Conclusão de Curso.
    2018.
    
    Script para obtenção de dados EMG da Myo Armband. Faz a captura de uma posição
    individual.
    
'''
import open_myo as myo
from sklearn.externals import joblib
import sys
import numpy as np
import threading
import time
import math

t = 0
primeira = 0
contagem = 1

#editável
posi = "Aberta"
quem = "Gio"
data = "_31_07_2018"
pasta = "coletaRAW/"
tipo = "_RAW_"
quant_amostras = 160
quant_vezes = 10

#não editável
nome_arquivo = pasta + quem + data + tipo + posi + ".npz"

#handler responsável por receber os dados
def process_emg(emg):

    global t
    global contagem

    '''dados vem em um vetor de 16 por caracteristica. Divide-se em 2, para
    2 vetores de 16'''
    emg0 = emg[0:8]
    emg1 = emg[8:16]

    #Verifica se foram coletadas todas as quantidades de amostra discriminada em "quant_amostras"
    if t < quant_amostras:
        t += 1
        #Necessário para salvar as primeiras amostras da sequência
        global primeira
        if primeira == 0:
            primeira = 1
            global amostra
            amostra = np.array([emg0])
            amostra = np.append(amostra, np.array([emg1]), axis=0)
        #Salva as outras amostras da sequência
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
            #Abre o arquivo da posição requerida. Caso não exista, cria este arquivo
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
            #Vibra para saber que será realizada a próxima amostra
            myo_device.services.vibrate(1)
            #Após pressionar ENTER, fara a próxima coleta (da mesma posição)
            input("Pressione ENTER para a proxima coleta")
            #Impede a Myo de entrar em deep sleep, e ocasionalmente falhar a comunicação
            myo_device.services.sleep_mode(1)
            print()
            print("Inicio da coleta: %d" % contagem)

#Captura o endereço MAC da Myo
myo_mac_addr = myo.get_myo()
print("MAC address: %s" % myo_mac_addr)

#Inicia um novo dispositivo Myo
myo_device = myo.Device()

#Previne que a pulseira entre em Sleep após certo tempo
myo_device.services.sleep_mode(1)

#Vibra a Myo para saber que conectou
myo_device.services.vibrate(1) # short vibration

#Verifica o nível de bateria da Myo
batt = myo_device.services.battery()
print("Battery level: %d" % batt)

#Habilita as notificações de EMG tipo RAW
myo_device.services.emg_raw_notifications()

#Seta o modo do EMG (RAW, IMU_OFF, CLASSIFIER_OFF)
myo_device.services.set_mode(myo.EmgMode.RAW, myo.ImuMode.OFF, myo.ClassifierMode.OFF)

#Adiciona o Handler recebe_emg ao pool de handlers EMG
myo_device.add_emg_event_handler(process_emg)

#Informações sobre o arquivo que será utilizado e início de coleta após pressionar ENTER
print("Nome do arquivo:" + nome_arquivo)
print()
input("Pressione ENTER para iniciar a coleta")
print()
print("Inicio da coleta: 1")

#Constante do while para o programa rodar até que mude para 0
Fim = True

while Fim:
    #Verifica se há alguma notificação de handler
    if myo_device.services.waitForNotifications(1):
        continue
    print("Waiting...")
