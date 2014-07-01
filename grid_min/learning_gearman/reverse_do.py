import gearman
#  setup client, connect to Gearman HQ
gm_client = gearman.GearmanClient(['127.0.0.1:59831'])
print 'Sending job...'
request = gm_client.submit_job('reverse', 'When the number of forces acting on a body produce no change in its state of rest or in motion, then the body is said to be in equilibrium.')
print "Result: " + request.result
