import gearman
import time
from pg_util import *
from parameters import *
import cStringIO
import csv

def generate_neighbors2(point,num_neigh_gen,increment):
	neighbor = set()
	pp = point[0]-increment
	hata_de = ''
	for i in range(3):
		qq=point[1]-increment
		for j in range(3):
			rr=point[2]-increment
			for k in range(3):
				ss=point[3]-increment
				for l in range(3):
					exp1 = pp>=-M_PI and pp<=M_PI
					exp2 = qq>=-M_PI and qq<=M_PI
					exp3 = rr>=-M_PI and rr<=M_PI
					exp4 = ss>=-M_PI and ss<=M_PI
					if exp1 and exp2 and exp3 and exp4:
						st = "{0},{1},{2},{3},{4},{5},{6}".format(pp,qq,rr,ss,0,0,point[6])
						neighbor.add(st)
						if pp-float(point[0])<0.00001 and qq-float(point[1])<0.00001 and rr-float(point[2])<0.00001 and ss-float(point[3])<0.00001:	
							hata_de=st
					ss+=increment
				rr+=increment
			qq+=increment
		pp+=increment
	neighbor.remove(hata_de)
	if len(neighbor)>num_neigh_gen:
		return [list(neighbor)[i] for i in range(num_neigh_gen)]
	else:
		return neighbor

def generate_neighbors(point,num_neigh_gen,increment):
        neighbor = set()
        pp = point[1]-increment
        hata_de = ''
        for i in range(3):
                qq=point[2]-increment
                for j in range(3):
                        rr=point[3]-increment
                        for k in range(3):
                                ss=point[4]-increment
                                for l in range(3):
                                        exp1 = pp>=-M_PI and pp<=M_PI
                                        exp2 = qq>=-M_PI and qq<=M_PI
                                        exp3 = rr>=-M_PI and rr<=M_PI
                                        exp4 = ss>=-M_PI and ss<=M_PI
                                        if exp1 and exp2 and exp3 and exp4:
                                                st = "{0},{1},{2},{3},{4},{5},{6}".format(pp,qq,rr,ss,0,0,int(point[7])+1)
                                                neighbor.add(st)
                                                if pp-float(point[1])<0.00001 and qq-float(point[2])<0.00001 and rr-float(point[3])<0.00001 and ss-float(point[4])<0.00001:
                                                        hata_de=st
                                        ss+=increment
                                rr+=increment
                        qq+=increment
                pp+=increment
        neighbor.remove(hata_de)
        if len(neighbor)>num_neigh_gen:
                return [str(i)+','+list(neighbor)[i]+','+str(point[8]) for i in range(num_neigh_gen)]
        else:
		ll=0
		while len(neighbor)<num_neigh_gen:
                	pt_to_gen=num_neigh_gen-len(neighbor)
			pts=generate_neighbors2([float(ptr) for ptr in list(neighbor)[ll].split(',')],pt_to_gen,increment)
			for i in pts:
				neighbor.add(i)
			ll+=1	
		return [str(i)+','+list(neighbor)[i]+','+str(point[8]) for i in range(num_neigh_gen)]

if __name__ == '__main__':
	conn = get_dbconn(param_dict['dbname'],
        	          param_dict['dbuser'],
                	  param_dict['dbhost'],
	                  param_dict['dbpass'])

	#Store the process ID of this program so that we can terminate it
	#whenever we want	
	st = "drop table if exists gm2_grid"
	execute_query(conn,st)
	st = "create table gm2_grid (pid int)"
	execute_query(conn,st)
	pid = os.getpid()
	st = "insert into gm2_grid values({0})".format(pid)
	execute_query(conn,st)
	
	#load initial points and send it to gearman
	cur = conn.cursor()
	st = "select * from gm2_values_to_run"
	cur.execute(st)
	
	#  setup client, connect to Gearman HQ
	gm_client = gearman.GearmanClient(['127.0.0.1:55559'])
	list_of_jobs = [dict(task="calculate_energy", data=",".join(map(str,list(i)))) for i in cur]
	print 'Sending job...'
	request = gm_client.submit_multiple_jobs(list_of_jobs,background=False, wait_until_complete=False)
	time.sleep(1.0)
	completed_requests = gm_client.wait_until_jobs_completed(request)
	cur.close()
	print "Computation of energies of initial points is complete..."

	st = "alter table gm2_values_to_run add column clus_num integer default 0"
	execute_query(conn,st)	
	#store the points that we need to explore
	cur = conn.cursor()
	st = "SELECT * FROM gm2_values_to_run ORDER BY energy limit {0}".format(num_energy_wells)
	cur.execute(st)
	explore_pts = [pt for pt in cur.fetchall()]
	cur.close()

	#parameters for grid_min
	grid_inc = increment
	prev_energy = 0.0
	curr_energy = 0.0
	clus_num = 0
	
	st = "drop table if exists gm2_cluster_pts"
	execute_query(conn,st)
	st = "create table gm2_cluster_pts(s_no integer, angle0 float, angle1 float, angle2 float, angle3 float, done integer, energy float, level integer, clus_num integer);"
        execute_query(conn,st)

	#grid minimization
	for point in explore_pts:
		st = "drop table if exists gm2_cluster{0}".format(clus_num)	
		execute_query(conn,st)
		st = "create table gm2_cluster{0}(s_no integer, angle0 float, angle1 float, angle2 float, angle3 float, done integer, energy float, level integer, clus_num integer);".format(clus_num)
		execute_query(conn,st)
		st = "insert into gm2_cluster{0} values({1},{2},{3},{4},{5},{6},{7},{8},{9})".format(clus_num,point[0],point[1],point[2],point[3],point[4],point[5],point[6],point[7],clus_num)
		execute_query(conn,st)
		curr_point = list(point)
		curr_point[8] = clus_num
		prev_energy = float(curr_point[6])
		curr_energy = prev_energy-1
		while (prev_energy-curr_energy>energy_threshold and grid_inc>0):
			st = "drop table if exists gm2_values_to_run"
			execute_query(conn,st)
			st = "create table gm2_values_to_run(s_no integer, angle0 float, angle1 float, angle2 float, angle3 float, done integer, energy float, level integer, clus_num integer);"
			execute_query(conn,st)
			neighbors = generate_neighbors(curr_point,num_pts,grid_inc)
			prev_energy = float(curr_point[6])
			output = cStringIO.StringIO() 
			writer = csv.writer(output)
	
        	        for neighbor in neighbors:
				val = [float(i) for i in neighbor.split(',')]
				val[0] = int(val[0])
				val[5] = int(val[5])
				val[7] = int(val[7])
                                val[8] = int(val[8])
		
                                writer.writerow(val)
                        
                	output.seek(0)
			cur = conn.cursor()
                	cur.copy_from(output,'gm2_values_to_run',sep=',',columns=('s_no','angle0','angle1','angle2','angle3','done','energy','level','clus_num'))
                	cur.close()
                	output.close()
                	conn.commit()
		
			#ready to compute energy values again
			print "starting gearman again...."

                	#setup client, connect to Gearman HQ
                	gm_client = gearman.GearmanClient(['127.0.0.1:55559'])
                	list_of_jobs = [dict(task="calculate_energy", data=neighbor) for neighbor in neighbors]
                	print 'Sending job...'
                	request = gm_client.submit_multiple_jobs(list_of_jobs,background=False, wait_until_complete=False)
                	time.sleep(1.0)
                	completed_requests = gm_client.wait_until_jobs_completed(request)
		
			#get the point with lowest energy for next iteration
			st = "select * from gm2_values_to_run order by energy limit 1"
			cur = conn.cursor()
			cur.execute(st)
			curr_point = cur.fetchone()
			cur.close()
			curr_energy = float(curr_point[6])
			st = "insert into gm2_cluster{0} (select * from gm2_values_to_run);".format(clus_num)
			execute_query(conn,st)
			grid_inc/=2
			print "Prev : {0}   Curr : {1}   grid_inc : {2}".format(prev_energy,curr_energy,grid_inc)
		print "Done for point {0}".format(clus_num)
		st = "delete from gm2_cluster{0} where energy<={1} or energy>={2}".format(clus_num,prev_energy-slack,prev_energy+slack)
		execute_query(conn,st)
		st = "insert into gm2_cluster_pts(select * from gm2_cluster{0})".format(clus_num)
		execute_query(conn,st)
		#st = "drop table if exists gm2_cluster{0}".format(clus_num)
		#execute_query(conn,st)
		prev_energy = 0.0
		curr_energy = 0.0
		grid_inc = increment
		clus_num+=1
	st = "drop table gm2_grid"
	execute_query(conn,st)
	st = "drop table if exists gm2_values_to_run"
        execute_query(conn,st)
	conn.commit()
	conn.close()
	
