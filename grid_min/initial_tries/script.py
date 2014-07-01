from math import *
from subprocess import call
import numpy as np
import decimal
increment=0.104719755
M_PI=3.141592654
pp=qq=-M_PI
global_write=open('energy.txt','w')
for i in range(60):
	for j in range(60):
		f=open('scripter','w')
		s='sed \'s/__angle1__/'+str(pp)+'/\' <temp >>temp1\n'
		f.write(s)
		f.write('rm temp\n')
		s='sed \'s/__angle2__/'+str(pp)+'/\' <temp1 >>temp\n'
                f.write(s)
		f.write('rm temp1\n')
		f.close()
		print pp,qq
		call("cp bkp temp",shell=True)
		call("chmod 755 scripter",shell=True)
		call("./scripter",shell=True)
		call("./run",shell=True)
		call("rm scripter",shell=True)
		call("rm temp",shell=True)
		call("./finder",shell=True)
		call("rm i.txt",shell=True)
		intere = [x.split('\t') for x in
          		open('a.txt','r').read().replace('\r','')[:-1].split('\n')]
		asd=intere[len(intere)-1][0].split()
		stst=str(pp)+'\t'+str(qq)+'\t'+str(asd[2])+'\n'
		global_write.write(stst)
		call("rm a.txt",shell=True)		
		qq+=increment
	qq=-M_PI
	pp+=increment
global_write.close()
