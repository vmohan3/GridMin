from math import *
from array import array
import numpy as np
import random
grid_step=6
grid_shrink_factor=2
next_wells=[]
doublearray=np.ones((360,360))
for i in range(60):
	for j in range(60):
		doublearray[i][j]=random.randrange(-100000,100000)
print doublearray
