import numpy as np

data = np.load("Gio_13_08_2018_RAW_Aberta.npz")

for key, value in data.items():
    np.savetxt("data.csv", value)
