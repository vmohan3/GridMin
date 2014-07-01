import cStringIO
import csv


csvdata = [-180, -180, -180, -180]
output = cStringIO.StringIO()
writer = csv.writer(output)
writer.writerow(csvdata)
output.write('hellooooo')
print output.getvalue()
