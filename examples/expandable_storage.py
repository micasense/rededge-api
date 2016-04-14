#Edit the following two variables to match your camera's ethernet IP for "host"
#and the path to your external storage device for "path"
#Please note the formatting, keep the "/" on the end
host = "http://192.168.1.83/"
path = "/home/pi/Desktop/test_pics/"

'''DO NOT edit anything below this line
----------------------------------------------------------------------------------------------
'''

import requests
import time
from datetime import datetime
import os
from natsort import natsorted

def main():    
    while(True): 
        r = wait_for_camera()
        rededge_file_transfer(r)

'''This method is the core of the program, containing the main loop which grabs
   files from the camera'''
def rededge_file_transfer(r):
    folder_index = []
    subfolder_count = 0
    try:
        print r.json()
        for n in range(0,len(r.json()['directories'])):
            folder_index.append(r.json()['directories'][n])
        print 'Unsorted: %s' % folder_index
        folder_index = natsorted(folder_index)
        print 'Sorted: %s' % folder_index
        while(len(folder_index) > 2):
            grab_everything_in_dir(folder_index[0])
            folder_index.pop(0)

        new_dir(path + folder_index[0])
        new_dir(path + folder_index[0] + "/%03d" % subfolder_count)
        startTime = datetime.now()

        while(True):
            tdelta = datetime.now() - startTime
            r = requests.get(host + "files/%s/%03d" % (folder_index[0], subfolder_count), timeout=1)
            print folder_index
            print r.json()
            #If the user has turned on the camera but taken no captures, wait
            if("Invalid file path" in r.text):
                print "Waiting for valid file path"
                time.sleep(1)
                continue
            #Check for image buffer
            if(len(r.json()['files']) > 10):
                get_captures(r, folder_index[0], subfolder_count)
                startTime = datetime.now()
            else:
                #Grab remaining captures
                if(tdelta.total_seconds() >= 30):
                    while(len(r.json()['files']) is not 0):
                        print "Captures left in folder: %s" % str(len(r.json()['files']))
                        get_captures(r, folder_index[0], subfolder_count)
                        r = requests.get(host + "files/%s/%03d" % (folder_index[0], subfolder_count), timeout=1)
                    s = requests.get(host + "files/%s" % folder_index[0], timeout=1)
                    #Check for multiple folders in the ####SET folder
                    if(len(s.json()['directories']) > (subfolder_count + 1)):
                        subfolder_count += 1
                        new_dir(path + folder_index[0] + "/%03d" % subfolder_count)
                    startTime = datetime.now()
                            
                else:
                    time.sleep(1)
                    continue
    except:
        #Wait for camera to respond if any error is encountered
        return

def wait_for_camera():
    while(True):
        try:
            r = requests.get(host + "files", timeout=1)
            return r
        except requests.exceptions.RequestException:
            print 'Waiting for camera response'

def get_captures(files, folder_index, subfolder_count, k=5):
    for n in range(0,k):
        r = requests.get(host + "files/%s/%03d/%s" % (folder_index, subfolder_count, files.json()['files'][n]['name']), stream=True)
        print files.json()['files'][n]['name']
        with open(path + "%s/%03d/%s" % (folder_index, subfolder_count, files.json()['files'][n]['name']), 'wb') as f:
            for chunk in r.iter_content(10240):
                f.write(chunk)
        r = requests.get(host + "deletefile/%s/%03d/%s" % (folder_index, subfolder_count, files.json()['files'][n]['name']))

def get_logs(files, folder_index):
    print 'Grabbing diag & paramlog'
    for n in range(0,2):
        r = requests.get(host + "files/%s/%s" % (folder_index, files.json()['files'][n]['name']), stream=True)
        print files.json()['files'][n]['name']
        with open(path + "%s/%s" % (folder_index, files.json()['files'][n]['name']), 'wb') as f:
            for chunk in r.iter_content(10240):
                f.write(chunk)
        r = requests.get(host + "deletefile/%s/%s" % (folder_index, files.json()['files'][n]['name'])) 

def new_dir(path):
    if not os.path.exists(path):
        os.mkdir(path)

def grab_everything_in_dir(folder_index):
    new_dir(path + folder_index)
    
    r = requests.get(host + 'files/%s' % folder_index)
    print r.json()
    print len(r.json()['directories'])
    if(len(r.json()['directories']) is not 0):
        for n in range(0, len(r.json()['directories'])):
            new_dir(path + folder_index + "/%03d" % n)
            time.sleep(0.5)
            s = requests.get(host + 'files/%s/%s' % (folder_index, r.json()['directories'][n]))
            if(len(s.json()['files']) is not 0):
                get_captures(s, folder_index, n, len(s.json()['files']))
            else:
                pass
    else:
        pass
    if(len(r.json()['files']) is not 0):
        get_logs(r, folder_index)
    else:
        pass

if __name__ == "__main__":
    main()
