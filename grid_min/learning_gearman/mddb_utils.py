import subprocess
import psycopg2
import time
import os

import parser as mddb_parser


import generate_peptides as genpep
import itertools

residue_dict = {
   'a':'ALA', 'r':'ARG', 'n':'ASN', 'd':'ASP',
   'c':'CYS', 'e':'GLU', 'q':'GLN', 'g':'GLY',
   'h':'HSP', #'x':'HSD', 'z': 'HSE',
   'i':'ILE', 'l':'LEU', 'k':'LYS',
   'm':'MET', 'f':'PHE', 'p':'PRO', 's':'SER',
   't':'THR', 'w':'TRP', 'y':'TYR', 'v':'VAL' }


def get_residues(protein_seq):
  residues = []
  prefix = None
  for c in protein_seq.lower():
    if c in ['*', '+']:
      prefix = c
    else:
      if prefix != None:
        residues = residues + [residue_dict[prefix+c]]
      else:
        residues = residues + [residue_dict[c]]                                                  
      prefix = None
  print protein_seq, " -> ", residues
  return residues

def mdq_push(conn, psp_terms, num_expjobs, num_iterations):

  terms_st = ','.join(map(lambda x: "'{0}'".format(x), psp_terms))
  d = {'num_expjobs':    num_expjobs, 
       'num_iterations': num_iterations,
       'expanded_terms': "'{}'::text[]",
       'rest_of_terms':  "array[{0}]".format(terms_st),
       'num_terms_left': len(psp_terms)
      }  


  st = """insert into MDQueue 
          (expanded_terms, rest_of_terms, num_terms_left, num_expjobs, num_iterations)
          values (
            {expanded_terms}, 
            {rest_of_terms}, 
            {num_terms_left}, 
            {num_expjobs}, 
            {num_iterations}
          )""".format(**d)

  execute_query(conn, st)


def load_sql(sql_file, dbname):
  some_options = "-X -q  -1 -v ON_ERROR_STOP=0 --pset pager=off"

  run_cmd("psql {0} -d {1} -f {2}".format(some_options, dbname, sql_file))

def run_sql(sql_cmd, dbname):
  some_options = "-X -q  -1 -v ON_ERROR_STOP=0 --pset pager=off"
  run_cmd("""psql {0} -d {1} -c "{2};" """.format(some_options, 
          dbname, sql_cmd))

def run_cmd(cmd):
  print cmd
  ret= subprocess.Popen(cmd, shell=True,
                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.read()
  print ret
  return ret

def run_cmd_background(cmd):
  print cmd
  subprocess.Popen(cmd, shell=True,
                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT)


def run_cmd_with_file(cmd, fn, log_fn):
  #print log_fn
  with open(log_fn, "w") as debug_log:
    print cmd, " < ", fn
    ret = ''
    with open(fn, 'r') as myinput:
      ret= subprocess.Popen(cmd, shell=True, stdin=myinput,
                     stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.read()
    debug_log.write(ret + "\n")
    #print ret
  return ret

def run_cmd_with_env(cmd, log_fn, my_env):
  print cmd

  with open(log_fn, "w") as debug_log:
    ret= subprocess.Popen(cmd, shell=True, env = my_env,
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.read()

    debug_log.write(ret + "\n")
  return ret

def get_dbconn(dbname, dbuser, dbhost, gp_pass):
  conn = None
  gp_pass = open(gp_pass, 'r').read()
  count = 1
  while conn == None:
    try:
      conn = psycopg2.connect(database=dbname, user=dbuser, host=dbhost,
                           password=gp_pass.decode('base64').decode('rot13'))
    except Exception, e:
      count = count + 1
      print "Trial {0}: {1}".format(count, e)
      time.sleep(1)
      conn = None

  print "Connected to ", dbname
  return conn

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

def pbe_split(st):
  st = st.strip()
  p, e = os.path.splitext(st)
  p, b = os.path.split(path)
  return p, b , e

def modify_namd_inp(in_fn, trj_id):
  path, ext = os.path.splitext(in_fn)
  out_fn = path + "." + str(trj_id) + ext
  lines = None
  with open(in_fn, 'r') as in_file:
    lines = in_file.readlines()
  st = 'coordinates'
  with open(out_fn, 'w') as out_file:
    for l in lines:
      if l.startswith(st):
        path, ext = os.path.splitext(l.split()[1])
        new_pdb_fn = path + "." + str(trj_id) + ext 
        out_file.write(st + "        " + new_pdb_fn+ "\n")
      else:
        out_file.write(l)
  return out_fn, new_pdb_fn


def run_charmm(charmm_in_fn):
  charmm_bin = '/damsl/mddb/software/MD/Charmm/c36b1/exec/gnu/charmm'
  st =run_cmd_with_file(charmm_bin, charmm_in_fn, charmm_in_fn+".log")
  return st

def load_protein(conn, c_id, p_id, in_path_name, prm_format):
  psf_dir,psf_fn = os.path.split(in_path_name)
  run_cmd("rm {0}/ch_*.csv".format(psf_dir))
  st = run_cmd('python simulation/parser.py --mode protein'+\
               ' --trjtop {0} --inputdir {1} --outputdir {2} --sim {3} ch 1'.format(psf_fn, psf_dir, psf_dir, prm_format))
  param_prefix = "{0}/ch_{1}".format(psf_dir, prm_format)
  execute_query(conn, "select load_protein({0},{1},'{2}')".format(
                c_id, p_id, param_prefix));


def simstart(param_dict):
  conn = get_dbconn(param_dict['dbname'],
                    param_dict['dbuser'],
                    param_dict['dbhost'],
                    param_dict['dbpass'])

  if param_dict['protein_seq'] != None:

    if param_dict['protein_seq'].lower() == 'aa':
      c_id = 2
    else:
      c_id = 1

    job_dict = genpep.generate_scripts({
      'dbpass':       param_dict['dbpass'],
      'dbhost':       param_dict['dbhost'],
      'dbuser':       param_dict['dbuser'],
      'dbname':       param_dict['dbname'],
      'prefix':       param_dict['prefix'] + "/" + param_dict['dbname'],
      'protein_seq':  param_dict['protein_seq'],
      'trj_id':       0
    })

    p_id = execute_query(conn,
                "select insert_new_protein(E'{0}', Null, Null)".format(param_dict['protein_seq']))

    print "creating parameter files", job_dict['psf_file_name']
    run_charmm(job_dict['minimization_in_fn'])
    prm_format = "charmm"
    load_protein(conn, c_id, p_id, job_dict['psf_file_name'], prm_format)

    ss_id = execute_query(conn, "select subspaces_insert({0}, {1}, '{2}', {3});".format(
                              c_id, p_id, param_dict['gmdhost'], param_dict['gmdport']))

    print "subspace_id: ", ss_id
    for _ in itertools.repeat(None, param_dict['num_expjobs']):
      e_id   = execute_query(conn,
                "select expjobs_insert({0},{1},{2},{3},{4},'{5}')".format(
                    ss_id,
                    param_dict['nstep_simulation'],
                    param_dict['timestep_pico'],
                    param_dict['trj_save_freq'],
                    param_dict['num_iterations'],
                    param_dict['simulator']))

      execute_query(conn, "select expjobs_activate({0})".format(e_id))
      #time.sleep(50)
  return ss_id




def latest_file(dir):
  files = [os.path.join(dir, fname) for fname in os.listdir(dir)]
  latest = max(files, key=os.path.getmtime)
  return latest
