import gearman
import time
from pg_util import *

conn = get_dbconn(param_dict['dbname'],
                  param_dict['dbuser'],
                  param_dict['dbhost'],
                  param_dict['dbpass'])

cur = conn.cursor()
st = "select * from values_to_run"
cur.execute(st)
#  setup client, connect to Gearman HQ
gm_client = gearman.GearmanClient(['127.0.0.1:55559'])
job_list = ['1,180,180,180,180,0', '2,-80,-10,60,-40,0', '3,80,10,-60,40,0', '4,10,20,30,40,0', '5,10,-20,-30,10,0']
list_of_jobs = [dict(task="calculate_energy", data=",".join(map(str,list(i)))) for i in cur.fetchall()]
print 'Sending job...'
request = gm_client.submit_multiple_jobs(list_of_jobs,background=False, wait_until_complete=False)
time.sleep(1.0)
completed_requests = gm_client.wait_until_jobs_completed(request)
for res in request:
	print "Calculated Energy? " + str(res.result)
cur.close()
conn.commit()
conn.close()
