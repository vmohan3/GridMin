from pg_util import *

conn = get_dbconn(param_dict['dbname'],
                  param_dict['dbuser'],
                  param_dict['dbhost'],
                  param_dict['dbpass'])

cur = conn.cursor()
st = "select * from gm2_worker"
cur.execute(st)
for record in cur.fetchall():
	cmd = "kill -9 {0}".format(record[0])
	run_cmd(cmd)
	st = "delete from gm2_worker where w_pid = {0}".format(record[0])
	execute_query(conn,st)
cur.close()
conn.commit()
conn.close()
