from subprocess import call
from optparse import OptionParser

if __name__ == '__main__':
	usage = "Usage: %prog [options] value"
	parser = OptionParser(usage=usage)
	parser.add_option("-w", "--num_worker", type="int", dest="num_worker",
                    default=None,
                    help="set the Number of workers to run", metavar="#NUM_WORKER")
	(options, args) = parser.parse_args()

	if options.num_worker==None:
		print "Error!!\nRe-run the program and enter the number of workers to start."
		os._exit(os.EX_DATAERR)

	for i in range(options.num_worker):
		cmd = "python energy_worker.py &"
		call(cmd, shell=True)	
