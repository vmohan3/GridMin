import os
import sys
import psycopg2
import datetime, time
import subprocess
try:
  mwd = os.environ['MDDBWORKDIR']
except:
  mwd = os.environ['HOME'] + "/mddb"

ubuntu_pythonpaths = "/damsl/software/python/ubuntu/lib/python2.7/site-packages/MDAnalysis-0.7.6-py2.7-linux-x86_64.egg/:/damsl/software/python/ubuntu/lib/python2.7/site-packages/:/usr/include/:/damsl/projects/molecules/software/tools/mddb/:{mddb_work_dir}/simulation/:{mddb_work_dir}/mddb/scheduler/".format(mddb_work_dir = mwd)

centos_pythonpaths = "/damsl/software/python/centos/lib/python2.6/site-packages/:/usr/include/:{mddb_work_dir}/scheduler/:{mddb_work_dir}/simulation/:/damsl/projects/molecules/software/tools/mddb/:/opt/greenplum-db/./lib/python".format(mddb_work_dir = mwd)

total_num_workers = 0

config_dir = '/damsl/mddb/data/mddb_configs'

param_dict = {
  'mode'        : 'cmd',
  'protein_seq' : None,
  'dbdir'       : '{mddb_work_dir}/database'.format(mddb_work_dir = mwd),
  'dbhost'      : 'mddb',
  'dbname'      : 'gridmin',
  'dbuser'      : os.environ['USER'],
  'gmdhost'     : 'mddb',
  'prefix'      : '/damsl/mddb/data',
  'numjobs'     : sys.maxint,
  'gmd'         : '/damsl/software/gearman/centos/sbin/gearmand',
  'gmw'         : '{mddb_work_dir}/scheduler/md_worker.py'.format(mddb_work_dir = mwd),
  'gearmansql'  : '/opt/greenplum/share/postgresql/contrib/pggearman.sql',
  'gmdport'     : 'rand',
  'madpack'     : '/usr/local/madlib/bin/madpack',
  'dbpass'      : 'mohan123!',
  'charmm_bin'  : '/damsl/mddb/software/MD/Charmm/c36b1/exec/gnu/charmm'
}

# Function for setting up the database
def setup_database():
  dbname = param_dict['dbname']
  dbdir = param_dict['dbdir']
  print "Setting up database ", dbname

# Function for executing the query
def execute_query(conn, st):
  cur = conn.cursor()
  print st
  cur.execute(st)
  retval = None
  try:
    retval = cur.fetchone()[0]
  except:
    pass

  cur.close()
  conn.commit()
  return retval

# Function for loading a sql file
def load_sql(sql_file, dbname):
  some_options = "-X -q  -1 -v ON_ERROR_STOP=0 --pset pager=off"

  run_cmd("psql {0} -d {1} -f {2}".format(some_options, dbname, sql_file))

# Function for running an sql command
def run_sql(sql_cmd, dbname):
  some_options = "-X -q  -1 -v ON_ERROR_STOP=0 --pset pager=off"
  run_cmd("""psql {0} -d {1} -c "{2};" """.format(some_options,
          dbname, sql_cmd))

# Function for running a command on shell
def run_cmd(cmd):
  print cmd
  ret= subprocess.Popen(cmd, shell=True,
                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.read()
  print ret
  return ret

# Function for creating a connection to the database
def get_dbconn(dbname, dbuser, dbhost, gp_pass):
  conn = None
  count = 1
  while conn == None:
    try:
      conn = psycopg2.connect(database=dbname, user=dbuser, host=dbhost,
                           password=gp_pass)
    except Exception, e:
      count = count + 1
      print "Trial {0}: {1}".format(count, e)
      time.sleep(1)
      conn = None

  print "Connected to ", dbname
  return conn


