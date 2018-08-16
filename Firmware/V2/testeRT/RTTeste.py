#  Copyright 2018 Alvaro Villoslada (Alvipe)
#  This file is part of Open Myo.
#  Open Myo is distributed under a GPL 3.0 license

from emgesture import fextraction as fex
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
import matplotlib.pyplot as plt
import pickle
import time
from sklearn.externals import joblib
import open_myo as myo

class_labels = list()

class_labels.append("aberta")
'''class_labels.append("polegar")
class_labels.append("indicador")
class_labels.append("medio")
class_labels.append("anelar")
class_labels.append("minimo")
class_labels.append("fechada")'''



count = 0

emg = list()

def process_emg(data):

    global count, emg, classifier, class_labels

    if count < 4:
        count += 1
        emg.append(np.array(data[0]))
        emg.append(np.array(data[1]))
    else:
        count = 0

        n_classes = 1
        n_iterations = 1
        n_channels = 8
        #n_signals = 8
        n_signals = n_classes * n_iterations * n_channels
        segmented_emg = list()

        print("EMG: ")
        print(emg)
        
        # Segmentation
        for n in range(n_signals):
            segmented_emg.append(fex.segmentation(emg[n], n_samples=1))

        # Feature calculation
        feature_list = [fex.mav, fex.rms, fex.var, fex.ssi, fex.zc, fex.wl, fex.ssc, fex.wamp]

        n_segments = len(segmented_emg[0][0])
        print("\nN_Segments: " + str(n_segments) + "\n")
        n_features = len(feature_list)
        feature_matrix = np.zeros((n_classes * n_iterations * n_segments, n_features * n_channels))
        n = 0

        print("Feature_Matrix_SHAPE: ")
        print(feature_matrix.shape)
        print("")

        print("Segmented_EMG: ")
        print(segmented_emg)
        print("")

        for i in range(0, n_classes):
            for j in range(n_segments):
                #print("i: " + str(i))

                #print("j: " + str(j))
                feature_matrix[n] = fex.features((segmented_emg[i][:, j],
                                                  segmented_emg[i + 1][:, j],
                                                  segmented_emg[i + 2][:, j],
                                                  segmented_emg[i + 3][:, j],
                                                  segmented_emg[i + 4][:, j],
                                                  segmented_emg[i + 5][:, j],
                                                  segmented_emg[i + 6][:, j],
                                                  segmented_emg[i + 7][:, j]), feature_list)
                n = n + 1

        # Target matrix generation
        print(feature_matrix)
        print(feature_matrix.shape)
        
        y = fex.generate_target(n_iterations*n_segments,class_labels)

        print(y)
        print(y.shape)

        # Dimensionality reduction and feature scaling
        [X,reductor,scaler] = fex.feature_scaling(feature_matrix, y)

        # Classification
        print(X)
        print(X.shape)
        
        predict = classifier.predict(feature_matrix)

        print(predict)
        emg = list()

classifier = joblib.load("ModelTesteMLP.pkl")


myo_device = myo.Device()
batt = myo_device.services.battery()
print("Nivel bateria Myo: %d" % batt)
myo_device.services.sleep_mode(1) # never sleep
myo_device.services.set_leds([0, 0, 255], [0, 0, 255])  # purple logo and bar LEDs)
myo_device.services.vibrate(1) # short vibration
# myo_device.services.emg_filt_notifications()
myo_device.services.emg_raw_notifications()
myo_device.services.set_mode(myo.EmgMode.RAW, myo.ImuMode.OFF, myo.ClassifierMode.OFF)
#myo_device.services.set_mode(myo.EmgMode.OFF, myo.ImuMode.OFF, myo.ClassifierMode.OFF)
time.sleep(1)
myo_device.add_emg_event_handler(process_emg)

while True:
    if myo_device.services.waitForNotifications(1):
        continue
    else:
        print("Waiting...")


#print("Classification accuracy = %0.5f." %(classifier.score(X_test,y_test)))

## Cross validation (optional; takes a lot of time)
#from sklearn.cross_validation import StratifiedShuffleSplit
#from sklearn.grid_search import GridSearchCV
#from sklearn.svm import SVC
#
#C_range = np.logspace(-5,5,11)
#gamma_range = np.logspace(-30,1,32)
#param_grid = dict(gamma=gamma_range,C=C_range)
#cv = StratifiedShuffleSplit(y, n_iter=20,test_size=0.2,random_state=42)
#grid = GridSearchCV(SVC(),param_grid=param_grid,cv=cv)
#grid.fit(X,y)
#print("The best parameters are %s with a score of %0.2f" % (grid.best_params_,grid.best_score_))


