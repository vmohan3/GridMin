import gearman
import time
from pg_util import *
from points_gen import increment,M_PI
from load_initial_points import num_pts
import cStringIO
import csv

def generate_neighbors(point,num_neigh_gen):
	neighbor = []
	pp = point[1]-increment
	sn = 1
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
						st = "{0},{1},{2},{3},{4},{5},{6},{7}".format(sn,pp,qq,rr,ss,0,0,point[7])
						neighbor.append(st)
						if int(pp)==int(point[1]) and int(qq)==int(point[2]) and int(rr)==int(point[3]) and int(ss)==int(point[4]):
							hata_de=st
					ss+=increment
					sn+=1
				rr+=increment
			qq+=increment
		pp+=increment
	neighbor.remove(hata_de)
	if len(neighbor)>num_neigh_gen:
		return [neighbor[i] for i in range(num_neigh_gen)]
	else:
		return neighbor

points_to_take = int(0.5*num_pts)

if __name__ == '__main__':
	conn = get_dbconn(param_dict['dbname'],
        	          param_dict['dbuser'],
                	  param_dict['dbhost'],
	                  param_dict['dbpass'])
	
	st = "drop table if exists grid"
	execute_query(conn,st)
	st = "create table grid (pid int)"
	execute_query(conn,st)
	pid = os.getpid()
	st = "insert into grid values({0})".format(pid)
	execute_query(conn,st)
	cur = conn.cursor()
	st = "select * from values_to_run"
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
	st = "drop table if exists cluster_points"
        execute_query(conn,st)
	st = "create table cluster_points as (select i.s_no,i.angle1,i.angle2,i.angle3,i.angle4,i.done,i.energy from init_config i,values_to_run v where v.s_no=i.s_no order by i.energy limit {0})".format(points_to_take)
	execute_query(conn,st)

	st = "alter table cluster_points add column cluster_number int"
	execute_query(conn,st)

	cur = conn.cursor()
	i=0
	cur.execute("select s_no from values_to_run")
	cur2 = conn.cursor()
	for sn in cur.fetchall():
		st = "update cluster_points set cluster_number={0} where s_no={1}".format(i,sn[0])
        	cur2.execute(st)
        	i+=1
	cur2.close()
	cur.close()
	conn.commit()

	#parameters for running and termination	
	threshold_iter = 20
	no_neg_pts = points_to_take
	no_neg_pts_threshold = 350
	st = "drop table if exists gen_neighbor_points"
	execute_query(conn,st)
	st = "create table gen_neighbor_points as (select * from cluster_points order by energy)"
        execute_query(conn,st)
	
	st = "alter table values_to_run add column cluster_number int default -1"
	execute_query(conn,st)
	print "Initiating main loop..."
 
	#main loop
	while threshold_iter>=0:
		score_total = 0.0
		total_gen = num_pts
		cur = conn.cursor()
		st = "select energy from gen_neighbor_points"
		cur.execute(st)
		for energy in cur.fetchall():
			score_total+=abs(energy[0])
		cur.close()
		
		cur = conn.cursor()
		st = "select * from gen_neighbor_points"
		cur.execute(st)
		
		diff = 0
		pts_for_this = 0
		looper = 0
		st = "delete from values_to_run"
		execute_query(conn,st)
		
		output = cStringIO.StringIO()
		writer = csv.writer(output)

		for record in cur.fetchall():
			if looper==(points_to_take-1):
				pts_for_this = num_pts-total_gen
			else:
				pts_for_this=int((abs(record[6])/score_total)*num_pts)
			neigh_pts = generate_neighbors(record,pts_for_this+diff)
			no_gen_neigh_pts = len(neigh_pts)
			diff = pts_for_this-no_gen_neigh_pts
			total_gen-=no_gen_neigh_pts
		
			for nnn in neigh_pts:
				val = [int(float(i)) for i in nnn.split(',')]
				writer.writerow(val)
			looper+=1
		output.seek(0)
		cur.close()
		
		st = "drop table if exists temp_neighbor"
		execute_query(conn,st)
		st = "create table temp_neighbor(s_no float, angle1 float, angle2 float, angle3 float, angle4 float, done integer, energy float, cluster_number integer);"
		execute_query(conn,st)

		cur = conn.cursor()
        	cur.copy_from(output,'temp_neighbor',sep=',',columns=('s_no','angle1','angle2','angle3','angle4','done','energy','cluster_number'))
        	cur.close()
		output.close()
		conn.commit()

		st = "insert into values_to_run(select i.s_no,i.angle1,i.angle2,i.angle3,i.angle4,i.done,i.energy,n.cluster_number from init_config i,temp_neighbor n where n.angle1 = i.angle1 and n.angle2 = i.angle2 and n.angle3 = i.angle3 and n.angle4 = i.angle4)"
		execute_query(conn,st)
		
		st = "drop table temp_neighbor"
		execute_query(conn,st)
		
		st = "create table temp_neighbor as (select distinct * from values_to_run)"
		execute_query(conn,st)

		st = "drop table values_to_run"
		execute_query(conn,st)
		
		st = "create table values_to_run as (select * from temp_neighbor)"
		execute_query(conn,st)

		st = "drop table temp_neighbor"
                execute_query(conn,st)

		st = "delete from values_to_run where done=1"
		execute_query(conn,st)
		
		cur = conn.cursor()
        	st = "select * from values_to_run"
        	cur.execute(st)

		print "starting gearman again...."

        	#  setup client, connect to Gearman HQ
        	gm_client = gearman.GearmanClient(['127.0.0.1:55559'])
        	list_of_jobs = [dict(task="calculate_energy", data=",".join(map(str,list(i)))) for i in cur]
        	print 'Sending job...'
        	request = gm_client.submit_multiple_jobs(list_of_jobs,background=False, wait_until_complete=False)
        	time.sleep(1.0)
        	completed_requests = gm_client.wait_until_jobs_completed(request)
        	cur.close()
		
		st = "delete from gen_neighbor_points"
		execute_query(conn,st)
		st = "insert into gen_neighbor_points(select i.s_no,i.angle1,i.angle2,i.angle3,i.angle4,i.done,i.energy,v.cluster_number from init_config i,values_to_run v where v.s_no=i.s_no order by energy limit {0})".format(points_to_take)
		execute_query(conn,st)
		st = "insert into cluster_points(select * from gen_neighbor_points)"
		execute_query(conn,st)
		currr = conn.cursor()
		st = "select count(*) from gen_neighbor_points where energy<0"
		currr.execute(st)
		no_neg_pts = currr.fetchone()[0]
		if no_neg_pts<no_neg_pts_threshold:
			threshold_iter-=1
		currr.close()
		conn.commit()
		print "One pass complete"
	
	st = "delete from cluster_points where energy>=0"
	execute_query(conn,st)
	st = "drop table gen_neighbor_points"
	execute_query(conn,st)
	st = "drop table grid"
	execute_query(conn,st)
	st = "drop table values_to_run"
        execute_query(conn,st)
	conn.commit()
	conn.close()
