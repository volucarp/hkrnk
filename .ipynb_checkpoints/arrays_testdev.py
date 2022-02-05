#%% mask setup
import numpy as np
mask = [[0, 1, 2], [1], [0, 1, 2]]
masky = np.array([0, 1, 2, 1, 0, 1, 2])
maskx = np.array([0, 0, 0, 1, 2, 2, 2])
npmask = np.array(mask)
y=np.arange(35).reshape(5,7)
res = y[maskx, masky]



