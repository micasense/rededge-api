import requests

gps_data = requests.get('http://192.168.10.254/gps')
print "Raw data : " + str(gps_data.json())
print "Has 3d fix: " + str(gps_data.json()['fix3d'])

capture = { 'store_capture' : True, 'block' : True }
r = requests.post("http://192.168.10.254/capture", data=capture)
print r.json()
