RedEdge Serial API
======================

This document describes the protocol which can be be used by software to control the RedEdge multi-spectral camera. The camera can be controlled using serial via the host connector. For more detailed information the physical connection to the camera, see the RedEdge Users's Guide.

Table of Contents
=================

{toc_here}


General Protocol Overview
=========================

The API is accessed via serial messages in the Mavlink format (see <http://en.wikipedia.org/wiki/MAVLink> and <http://qgroundcontrol.org/mavlink>). Mavlink provides an open data format for interaction as well as a suite of tools to assist the programmer in developing and testing the interface.  RedEdge uses Mavlink v1.0 messages and communicates with the host at 57600 baud.  The camera currently does not provide status back to the host, but accepts host GPS and orientation information over the serial interface. 

The messages defined below can be sent from the host vehicle to the RedEdge camera. For the sake of bevity, we do not define the messages here. See the Mavlink message definitions at <http://pixhawk.ethz.ch/mavlink/> for message specifics. Listed below are exceptions and recommendations for the use of the standard message definitions.

The PING message can be used to ensure round-trip serial connectivity with the RedEdge.

Receipt of serial state messages will override any RedEdge internal or external sensor data, such as a connected GPS, for 30 seconds since the last state message was received.  For aircraft state and mount status, messages should be sent as often as possible to ensure the latest state information is available to the camera when a capture is taken.

Specifically, messages defined in mavlink/message_definitions/ardupilotmega.xml are used. Ardupilotmega.xml includes common.xml, so compiling it should create the required headers. For C/C++, use the mavgenerate.py tool to generate the headers from ardupilotmega.xml, then include common/mavlink.h and ardupilotmega/mavlink.h in your C/C++ project. Python bindings can be used as well, and are found in the mavlink/pymavlink directory. 

Messages
========

## HEARTBEAT

The RedEdge will send a heartbeat message approximately once per second using the component ID MAV\_COMP\_ID\_CAMERA. While this message can be safely ignored, it can be used to verify the RedEdge is properly powered on.

<http://pixhawk.ethz.ch/mavlink/#HEARTBEAT>

## PING

Send the PING message with system\_id = 0 and component\_id = 0, and with a new sequence number each time, to ensure round-trip communications with the RedEdge.  The PING message will be responded to with the same sequence number and the system\_id and component\_id of the sender (which are present in the message header).

## GPS\_RAW\_INT

Use this message to send the raw GPS information to the RedEdge as received by the host vehicle. This is the main message providing GPS information to the RedEdge. Forwarding GPS data to the camera as soon as it is received by the host will ensure the latest information is present in a new capture.  Use the 64-bit time_usec field to set the camera's UTC time.

<http://pixhawk.ethz.ch/mavlink/#GPS_RAW_INT>

## SYSTEM\_TIME

This message is required if using GLOBAL\_POSITION\_INT, as that message does not provide a UTC timestamp.  It is used to update UTC time to provide accurate timestamping of images. Provide a 64-bit unix timestamp referenced to UTC time and the UNIX (not GPS) epoch.  Most GPS receivers provide this information in a UTC time message.

Note: if using GPS\_RAW\_INT, the 64bit timestamp should be set to UTC time prior to sending.

<http://pixhawk.ethz.ch/mavlink/#SYSTEM_TIME>

## ATTITUDE

Vehicle state (roll, pitch, yaw) and vehicle rates can be provided via the ATTITUDE message.  Note that this is the state of the host vehicle. The offset of the camera from the host reference frame, whether fixed or on a gimbals, should be provided via the MOUNT_STATUS message defined below.

<http://pixhawk.ethz.ch/mavlink/#ATTITUDE>

## MOUNT_STATUS

This message definition is difficult to find, so we will repeat it here.  It has 3 values, sent in degrees *100.

```
@param pointing_a - pitch rotation (INT16, deg*100)
@param pointing_b - roll rotation (INT16, deg*100)
@param pointing_c - yaw rotation (INT16, deg*100)
```

The three pointing values represent the orientation of a gimbals. The RedEdge interprets these numbers as a set of rotations in roll, then pitch, then yaw, to rotate from the camera pointing directly forward (along the aircraft X axis) to the current camera orientation relative to the aircraft.  Each rotation is relative to the axis pointing out of the front of the camera (coaxial with the lenses) after performing the previous rotation.  Positive values are right handed rotations, while negative values are left-handed. Positive pitch is defined as a rotation where the camera points up, so a standard camera orientation will have a negative pitch rotation.

For example, values of -90 pitch, -90 yaw, 0 roll might be used.  Starting with the camera pointed forward in the same direction as the aircraft's nose, we rotate 0 degrees in roll, causing no movement. Next we rotate -90 degrees in pitch, so that the camera is oriented straight down. Next, we rotate -90 degrees in the camera's yaw axis. The camera now pointed out of the aircraft's left wing, with the right edge of the camera toward the sky and the top toward the front of the aircraft.

For a two-axis gimbals where the camera is generally pointed straight down and the two gimballed axes are aircraft pitch and roll, the two values can be derived directly from the gimbals rotation. Pitch will generally be close to -90, while roll and yaw will be close to zero.

The combination of the aircraft attitude sent in the attitude message and the rotations in the mount status message will be used to derive an earth-fixed camera orientation.  It is recommended that when these messages are built, the values for both the aircraft orientation and the gimbals orientation are latched into memory, then they are sent via these messages. This will ensure that the aircraft orientation and gimbals orientations were acquired at the same moment. 

Note: For a fixed camera pointed straight down relative to the aircraft, and with the top of the camera toward the front of the aircraft, use (pitch = -90.0, roll = 0, yaw = 0)

## GLOBAL\_POSITION\_INT

Used to update the position from a host state estimate using more than raw GPS, such as a GPS-aided INS system.  This may not be the position provided by the GPS receiver, but may be more accurate and/or updated more frequently. Since this message does not have a fix status field, sending it will imply a 3D GPS fix.

<http://pixhawk.ethz.ch/mavlink/#GLOBAL_POSITION_INT>

## GPS\_STATUS

GPS satellite infomation which is updated on the RedEdge WiFi user interface.  This message is not required, but if sent the GPS status bars on the RedEdge WiFi interface will be updated. 

<http://pixhawk.ethz.ch/mavlink/#GPS_STATUS>



