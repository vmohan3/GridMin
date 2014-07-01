from optparse import OptionParser
import json
import gearman 
import socket
from pg_util import *

# Setup gearman server and worker by
# - getting a random port number within a range of [50000,59999];
# - starting a gearman server using that port number
# - connecting a gearman charmm worker to that port

def setup_gearman():
  global total_num_workers
  gmdport = param_dict['gmdport']
  if (gmdport == 'rand'):
    gmdport = random.randint(50000,59999)
    param_dict['gmdport'] = str(gmdport)

  print "Gearman server\'s port number: {0}".format(param_dict['gmdport'])
  gmdlog="/home/vmohan3/{0}_{1}_gearmanlog".format(param_dict['dbuser'],param_dict['dbname'])
  param_dict['gmdlog'] = gmdlog


  run_sql("drop table if exists gmqueue", param_dict['dbname'])

  gearman_st = "{gmd} --daemon -l {gmdlog} --verbose DEBUG " +\
               "--port {gmdport} " +\
               "--libpq-conninfo 'hostaddr=127.0.0.1 port=5432 dbname={dbname} user={dbuser}' " +\
               "--libpq-table=gmqueue -q Postgres"


  mddb_utils.run_cmd(gearman_st.format(**param_dict))

  time.sleep(1)

  conn = get_dbconn(param_dict['dbname'],
                    param_dict['dbuser'],
                    param_dict['dbhost'],
                    param_dict['dbpass'])

  cur = conn.cursor()
  cur.execute("select gw_host,num_workers,task_id from ClusterConfig")

  for (h,num_workers,task_id) in cur:
    pythonpaths = centos_pythonpaths if h == 'mddb' else ubuntu_pythonpaths
    param_dict['gmwhost'] = h
    param_dict['gpu_option'] = '-g' if h == 'mddb-gpu' else ''
    param_dict['pythonpaths'] = pythonpaths
    param_dict['task_id'] = task_id
    param_dict['remotegen'] = ""

    actual_host = h
    if h in ['hhpc'] or 'dsp' in h:
      h = 'mddb'
      param_dict['remotegen'] = '--remotegen {0}'.format(actual_host)

    #combo_template = minicombo if h == 'mddb' else supercombo
    for _ in itertools.repeat(None, num_workers):
      i = mddb_utils.execute_query(conn, "select workers_insert('{0}');".format(actual_host))
      param_dict['gw_sn']  = i
      param_dict['gmwscreen'] = "gmw_{0}_{1}_{2}_{3}".format(param_dict['dbname'], actual_host, i,task_id)
      start_gmw(conn,param_dict)

    total_num_workers = num_workers + total_num_workers

  conn.commit()
  conn.close()

class CustomGearmanWorker(gearman.GearmanWorker):
    def set_stop(self):
        self.stop = True

    def on_job_execute(self, current_job):
        print "Job started"
        return super(CustomGearmanWorker, self).on_job_execute(current_job)

    def on_job_exception(self, current_job, exc_info):
        print "Job failed, CAN stop last gasp GEARMAN_COMMAND_WORK_FAIL", exc_info
        traceback.print_exc()
        return super(CustomGearmanWorker, self).on_job_exception(current_job, exc_info)

    def on_job_complete(self, current_job, job_result):
        print "Job completed"
        return super(CustomGearmanWorker, self).send_job_complete(current_job, job_result)

    def after_poll(self, any_activity):
        if 'stop' in vars(self).keys():
          return False
        else:
          return True

gmdhost = None
gpu_id = None

#using the functions defined above
if __name__ == '__main__':
	#gearman

	dbname = param_dict['dbname']
	dbhost = param_dict['dbhost']
	dbuser = param_dict['dbuser']
	dbpass = param_dict['dbpass']
	
	print "Starting up a gearman worker."

	usage = "Usage: %prog [options] <config file>"
	parser = OptionParser(usage=usage)
	parser.add_option("-s", "--server", type="string", dest="server",
                    default="",
                    help="set the Gearman server IP", metavar="#SERVER")

	parser.add_option("-c", "--client", type="string", dest="client_id",
                    default="charmm_worker",
                    help="set the worker client id", metavar="#CLIENTID")
	
	parser.add_option("-t", "--task_id", type="string", dest="task_id",
                    default="straight_md",
                    help="set the worker task id", metavar="#TASKID")

	parser.add_option("-n", "--name", type="string", dest="worker_name",
                    default='',
                    help="set the worker name", metavar="#NAME")

	parser.add_option("--gw_sn", type="int", dest="gw_sn",
                    default=None,
                    help="set the worker serial number", metavar="#GMWSN")

	parser.add_option("--gmdhost", type="string", dest="gmdhost",
                    default='',
                    help="set the gearman host", metavar="#GMDHOST")
	
	parser.add_option("--gmdport", type="string", dest="gmdport",
                    default='',
                    help="set the gearman port", metavar="#GMDPORT")

	parser.add_option("-m", "--mode", type="string", dest="mode",
                    default='load',
                    help="specify the running mode: sim/load", metavar="#MODE")

	(options, args) = parser.parse_args()

	if len(options.server) < 1:
		parser.error("No server specified")

	mode = options.mode
	task_id = options.task_id
	
	worker_name = options.worker_name
	
	worker = CustomGearmanWorker([options.server])
	
	worker.set_client_id(options.client_id)

	#worker.register_task(task_id, process_work)
	#print "Worker connected"
	gmdhost = options.gmdhost
	gmdport = options.gmdport
	
	hostname = socket.gethostname()
	gw_process_id = os.getpid();
	print gw_process_id

	conn = get_dbconn(dbname, dbuser, dbhost, dbpass)
	cur = conn.cursor()
	st = "update Workers set gw_name = '{0}', process_id = {2} where gw_sn = {1}".format(
         worker_name, options.gw_sn, gw_process_id
       )
	print st
	sys.stdout.flush()
	#cur.execute(st)
	cur.close()
	conn.commit()
	conn.close()
	worker.work()
