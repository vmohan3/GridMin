from pg_util import *
from parameters import *
import cStringIO
import csv

pp=qq=rr=ss=-M_PI
output = cStringIO.StringIO()
writer = csv.writer(output)

if __name__ == '__main__':
	setup_database()
        conn = get_dbconn(param_dict['dbname'],
                          param_dict['dbuser'],
                          param_dict['dbhost'],
                          param_dict['dbpass'])

        st = "drop table if exists gm2_init_config"
        execute_query(conn,st)
        st = "create table gm2_init_config(s_no integer, angle0 float, angle1 float, angle2 float, angle3 float, done integer, energy float, level integer);"
        execute_query(conn,st)
	pp=-M_PI
        sn=1
        for i in range(iter):
                qq=-M_PI
                for j in range(iter):
                        rr=-M_PI
                        for k in range(iter):
                                ss=-M_PI
                                for l in range(iter):
                                        val = [sn,pp,qq,rr,ss,0,0,0]
                                        print val
                                        writer.writerow(val)
                                        ss+=increment
                                        sn+=1
                                rr+=increment
                        qq+=increment
                pp+=increment                   
        output.seek(0)
        cur = conn.cursor()
	cur.copy_from(output,'gm2_init_config',sep=',',columns=('s_no','angle0','angle1','angle2','angle3','done','energy','level'))
        cur.close()
	output.close()
        print "Done loading initial values to database."
	conn.commit()
	conn.close()
