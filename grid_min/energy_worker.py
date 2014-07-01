import gearman
from subprocess import call
from pg_util import *

gm_worker = gearman.GearmanWorker(['127.0.0.1:55559'])
conn = get_dbconn(param_dict['dbname'],
                  param_dict['dbuser'],
                  param_dict['dbhost'],
                  param_dict['dbpass'])


#  define method to calculate 'energy'
def task_listener_calculate_energy(gearman_worker, gearman_job):
	print 'Computing Energy Value.....'
	angles=gearman_job.data.split(',')
	script_name='scripter_'+str(angles[0])
	temp='temp_'+str(angles[0])
	temp1='temp1_'+str(angles[0])
	f=open(script_name,'w')
	s='sed \'s/__angle1__/'+str(angles[1])+'/\' <'+temp+' >>'+temp1+'\n'
	f.write(s)
	f.write('rm '+temp+'\n')
	s='sed \'s/__angle2__/'+str(angles[2])+'/\' <'+temp1+' >>'+temp+'\n'
	f.write(s)
	f.write('rm '+temp1+'\n')
	s='sed \'s/__angle3__/'+str(angles[3])+'/\' <'+temp+' >>'+temp1+'\n'
	f.write(s)
	f.write('rm '+temp+'\n')
	s='sed \'s/__angle4__/'+str(angles[4])+'/\' <'+temp1+' >>'+temp+'\n'
	f.write(s)
	f.write('rm '+temp1+'\n')
	f.close()
	cmd = "cp bkp "+temp
	call(cmd,shell=True)
	cmd = "chmod 755 "+script_name
        call(cmd,shell=True)
	cmd = "./"+script_name
        call(cmd,shell=True)
	cmd = "charmm <"+temp+" >>i_"+str(angles[0])+".txt"
        call(cmd,shell=True)
	cmd = "rm "+script_name
	call(cmd,shell=True)
	cmd = "rm "+temp
	call(cmd,shell=True)
	cmd = "grep \"ABNR>\" i_"+str(angles[0])+".txt >>a_"+str(angles[0])+".txt"
	call(cmd,shell=True)
	cmd = "rm i_"+str(angles[0])+".txt"
	call(cmd,shell=True)
	file_name = "a_"+str(angles[0])+".txt"
	intere = [x.split('\t') for x in open(file_name,'r').read().replace('\r','')[:-1].split('\n')]
        asd=intere[len(intere)-1][0].split()
	

	conn2 = get_dbconn(param_dict['dbname'],
                  	   param_dict['dbuser'],
                           param_dict['dbhost'],
                           param_dict['dbpass'])

	st = "update init_config set energy = {0} where angle1 = {1} and angle2 = {2} and angle3 = {3} and angle4 = {4}".format(asd[2],angles[1],angles[2],angles[3],angles[4])
	execute_query(conn2,st)

	st = "update init_config set done = {0} where angle1 = {1} and angle2 = {2} and angle3 = {3} and angle4 = {4}".format(1,angles[1],angles[2],angles[3],angles[4])
        execute_query(conn2,st)
	
	conn2.commit()
	conn2.close()
	cmd = "rm {0}".format(file_name)
	call(cmd,shell=True)
	return asd[2]

gearman_pid = os.getpid()
st = "insert into worker values ({0},'calculate_energy')".format(gearman_pid)
execute_query(conn,st)
gm_worker.set_client_id('Worker # 1')
gm_worker.register_task('calculate_energy', task_listener_calculate_energy)
conn.commit()
conn.close()
gm_worker.work()
