#!/usr/bin/env python

##################################################################################
# The MIT License (MIT)
# 
# Copyright (c) 2015 MicaSense, Inc.
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
##################################################################################

import sys, time
from pymavlink import mavutil
from argparse import ArgumentParser

parser = ArgumentParser(description=__doc__)
parser.add_argument("--baudrate", type=int, help="master port baud rate", default=115200)
parser.add_argument("--device", default="/dev/ttyUSB0", help="serial device")
args = parser.parse_args()

master = mavutil.mavlink_connection(args.device, baud=args.baudrate)

MAV_COMP_ID_CAMERA = 100

# Wait to receive a heartbeat from the camera
print("Waiting for HEARTBEAT...")
msg = master.recv_match(type='HEARTBEAT', blocking=True)
print("Heartbeat received from system %u, component %u" % (master.target_system, master.target_component))
if (master.target_component != MAV_COMP_ID_CAMERA):
   print "Received heartbeat, but it wasn't from the camera. Exiting"
   exit()

MAVLINK_FIX_TYPE_3D = 3
ping_seq = 0

while True:
   print ("[%f] Sending messages: GPS_RAW_INT, MOUNT_STATUS, ATTITUDE") % (time.time())
   
   gps_lat_deg = 33; 
   gps_lon_deg = -100; 
   gps_alt_m = 1000
   gps_eph = 1.5; 
   gps_epv = 2.5; 
   gps_vel_m_per_s = 3.5; 
   gps_course_deg = 45; 
   gps_sats_vis = 20
   master.mav.gps_raw_int_send(int(time.time()*1e6), 
                               MAVLINK_FIX_TYPE_3D, 
                               int(gps_lat_deg*1e7), 
                               int( gps_lon_deg*1e7), 
                               int(gps_alt_m*1e3), 
                               int(gps_eph*1e2), 
                               int(gps_epv*1e2), 
                               int(gps_vel_m_per_s*1e2), 
                               int(gps_course_deg*1e2), 
                               gps_sats_vis)
   
   mount_offset_a = 1.1
   mount_offset_b = 2.2
   mount_offset_c = -3.3
   master.mav.mount_status_send(master.target_system, 
                                master.target_component,  
                                int(mount_offset_a*100), 
                                int(mount_offset_b*100), 
                                int(mount_offset_c*100))

   aircraft_roll_deg = 1.1; 
   aircraft_pitch_deg = 2.2; 
   aircraft_yaw_deg = -3.3;
   aircraft_roll_rate_deg_sec = 4.4; 
   aircraft_pitch_rate_deg_sec = 5.5; 
   aircraft_yaw_rate_deg_sec = -6.6
   master.mav.attitude_send( int(time.time()*1e3)%2^16, 
                             aircraft_roll_deg, 
                             aircraft_pitch_deg, 
                             aircraft_yaw_deg, 
                             aircraft_roll_rate_deg_sec, 
                             aircraft_pitch_rate_deg_sec, 
                             aircraft_yaw_rate_deg_sec)
   
   # Send a ping message to the camera and wait for a response
   # This ensures that we have communications both ways
   ping_seq = ping_seq + 1;
   print ("[%f] Sending messages: PING, waiting for response") % (time.time())
   t1 = time.time()
   master.mav.ping_send(int(t1*1e6), ping_seq%255, 0, 0)
   msg = master.recv_match(type='PING', blocking=True)
   t2 = time.time()
   print ("[%f] PING Response received, roundtrip time %f sec") % (time.time(), t2-t1)
   
   
