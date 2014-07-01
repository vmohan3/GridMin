from math import *
import pylab as p
import matplotlib.pyplot as plt
import numpy as np
intere = [x.split('\t') for x in
          open('energies.txt','r').read().replace('\r','')[:-1].split('\n')]
data = np.array(map(list,intere), dtype='float')
datum=data[:,2]
data=np.array(datum).reshape(61,61)
print data
plt.imshow (data, extent=[-180,180,-180,180], origin='lower', interpolation='nearest', vmin = 0, vmax = 1 )
plt.colorbar()
plt.show()
