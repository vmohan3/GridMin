from pg_util import *
from parameters import *

if __name__ == '__main__':
	print "Generating initial {0} points".format(num_pts)
        setup_database()
        conn = get_dbconn(param_dict['dbname'],
                          param_dict['dbuser'],
                          param_dict['dbhost'],
                          param_dict['dbpass'])
	st = "drop table if exists gm2_values_to_run"
        execute_query(conn,st)

	for i in range(num_part):
		st=''
		if i==0:
        		st = "create table gm2_values_to_run as(SELECT DISTINCT * FROM(SELECT {0} + floor(random()*{1})::integer AS s_no FROM generate_series(1, {2}) g GROUP  BY 1) r JOIN gm2_init_config USING (s_no) LIMIT {3})".format('1',str(span),str(points_per_partition+500), points_per_partition)

		elif i==(num_part-1):
			st="insert into gm2_values_to_run(SELECT DISTINCT * FROM (SELECT {0} + floor(random() * {1})::integer AS s_no FROM generate_series(1, {2}) g GROUP  BY 1 ) r JOIN gm2_init_config USING (s_no) LIMIT {3})".format(str(i*span),str(total_points-i*span),str(points_per_partition+500), points_per_partition)

		else:
			st="insert into gm2_values_to_run (SELECT DISTINCT * FROM  (SELECT {0} + floor(random() * {1})::integer AS s_no FROM generate_series(1, {2}) g GROUP  BY 1 ) r JOIN gm2_init_config USING (s_no) LIMIT  {3})".format(str(i*span),str(span),str(points_per_partition+500), points_per_partition)
        	execute_query(conn,st)
	conn.commit()
	conn.close()
