import gearman
import time
#  setup client, connect to Gearman HQ
gm_client = gearman.GearmanClient(['127.0.0.1'])
list_of_jobs = [dict(task="reverse", data="Hello"), dict(task="reverse", data="vaibhav")]
print 'Sending job...'
request = gm_client.submit_multiple_jobs(list_of_jobs,background=False, wait_until_complete=False)
time.sleep(1.0)
completed_requests = gm_client.wait_until_jobs_completed(request, poll_timeout=5.0)
#for completed_job_request in completed_requests:
#	check_request_status(completed_job_request)
for res in request:
	print "Result : " + res.result
