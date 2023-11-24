from attendance.models import ProjectConfiguration, ClassAttendance, FalseAttemptGeoLocation

import csv
file_path = 'example.csv'
cf=open(file_path, 'w', newline='')
csv_writer = csv.writer(cf)

csv_writer.writerow(['mail', 'lat', 'lon', 'accuracy'])

i=0
for f in FalseAttemptGeoLocation.objects.all():
    csv_writer.writerow([f.student.mail,f.lat,f.lon,f.accuracy])
    if i%100==0:
        print(i)
    i+=1

