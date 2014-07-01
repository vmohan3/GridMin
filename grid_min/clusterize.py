from pg_util import *
import math

#metric can be euclidean, manhattan or minkowski
metrics = 'euclidean'

def minkowski(point1,point2,p):
        assert len(point1) == len(point2)
        sum = 0.0
        for i in range(len(point1)):
                sum+=math.pow(math.abs(point1[i]-point2[i]),p)  
        return math.pow(sum,1/p)

def distance(metric, point1, point2, p=3):
	if metric == 'euclidean':
		return minkowski(point1,point2,2)
	elif metric == 'manhattan':
		return minkowski(point1,point2,1)
	else:
		return minkowski(point1,point2,p)

if __name__=='__main__':
	conn = get_dbconn(param_dict['dbname'],
	                  param_dict['dbuser'],
        	          param_dict['dbhost'],
                	  param_dict['dbpass'])
	cur = conn.cursor()
	st = "select * from cluster_points order by cluster_number"
	print st
	cur.execute(st)
	clusters = dict()
	for record in cur.fetchall():
		pt = [record[i] for i in range(len(record)-1)]
		cls = int(record[len(record)-1])
		if cls in clusters:
			if pt not in clusters[cls]:
				clusters[cls].append(pt)
		else:
			clusters.setdefault(cls,[])
			clusters[cls].append(pt)
	
	retain = list(clusters.keys())

	curr_keys = list(clusters.keys())
	while len(curr_keys)>0:
		key = curr_keys.pop()
		for point in clusters[key]:
			check_keys = clusters.keys()
			check_keys.remove(key)
			for ptr in check_keys:
				if point in clusters[ptr]:
					clusters[key].append(clusters[ptr])
					del clusters[ptr]
					curr_keys.remove(ptr)
	now = list(clusters.keys())
	ctr = 0
	for pts in retain:
		if pts not in now:
			print pts
			ctr+=1

	print "Total clusters merged : {0}".format(ctr)
	cur.close()
	conn.commit()
	conn.close()
