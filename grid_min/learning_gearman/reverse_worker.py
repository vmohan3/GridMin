import gearman
gm_worker = gearman.GearmanWorker(['127.0.0.1'])
#  define method to handled 'reverse' work
def task_listener_reverse(gearman_worker, gearman_job):
	print 'reporting status'
	return gearman_job.data[::-1]

gm_worker.set_client_id('Worker # 1')
gm_worker.register_task('reverse', task_listener_reverse)
gm_worker.work()
