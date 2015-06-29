#!/usr/bin/env python
# vim:set ts=4 sw=4 et:
#
# Copyright 2014 Vladimir Ermakov.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License
# for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

import argparse
import socket
import rospy
from mavros.utils import *
from mavros.param import *
from mavros.srv import CommandBool
import serial
import time

def get_param_file_io(args):
    if args.mission_planner:
        print_if(args.verbose, "MissionPlanner format")
        return MissionPlannerParam(args)

    elif args.qgroundcontrol:
        print_if(args.verbose, "QGroundControl format")
        return QGroundControlParam(args)

    else:
        if args.file.name.endswith('.txt'):
            print_if(args.verbose, "Suggestion: QGroundControl format")
            return QGroundControlParam(args)
        else:
            print_if(args.verbose, "Suggestion: MissionPlanner format")
            return MissionPlannerParam(args)


def do_load(args):
    rospy.init_node("mavmission", anonymous=True)

    param_file = get_param_file_io(args)
    with args.file:
        param_transfered = param_set_list(param_file.read(args.file), args.mavros_ns)

    print_if(args.verbose, "Parameters transfered:", param_transfered)


def do_dump(args):
    rospy.init_node("mavmission", anonymous=True)

    param_received, param_list = param_get_all(args.force, args.mavros_ns)
    print_if(args.verbose, "Parameters received:", param_received)

    param_file = get_param_file_io(args)
    with args.file:
        param_file.write(args.file, param_list)


def do_get(args):
    rospy.init_node("mavmission", anonymous=True)

    print(param_get(args.param_id, args.mavros_ns))
    print(args.param_id)
    print(args.mavros_ns)
     

def do_set(args):
    rospy.init_node("mavmission", anonymous=True)

    if '.' in args.value:
        val = float(args.value)
    else:
        val = int(args.value)

    print(param_set(args.param_id, val, args.mavros_ns))


def do_start(args):
    rospy.init_node("mavmission", anonymous=True)
    ser = serial.Serial('/dev/ttyUSB0',9600)
    while 1:
     try:
       serial_data=ser.readline()
       print serial_data

       serial_data_divide=serial_data.split(',')
       del_x=int(serial_data_divide[0])
       del_y=int(serial_data_divide[1])
       del_z=int(serial_data_divide[2])
       print del_x
       print del_y
       print del_z
       
       print(param_set("TANKER_DEL_X",del_x,args.mavros_ns))
       print(param_set("TANKER_DEL_Y",del_y,args.mavros_ns))
       print(param_set("TANKER_DEL_Z",del_z,args.mavros_ns))
       print time.time()
     except KeyboardInterrupt:
       print "Keyboard interrupt"
       break
     except:
       print "error"
#       print(param_set("TANKER_DEL_X",0,args.mavros_ns))
#       print(param_set("TANKER_DEL_Y",0,args.mavros_ns))
#       print(param_set("TANKER_DEL_Z",0,args.mavros_ns))

#    host=''
#    port=10000
#    s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
#    s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
#    s.setsockopt(socket.SOL_SOCKET,socket.SO_BROADCAST,1)
#    s.bind((host,port))
#    while 1:
#     try:
#      UDP_data,addr=s.recvfrom(1024)
#      print "got data from",addr
#      s.sendto("broadcasting",addr)
#      print UDP_data
#      value=int(UDP_data)
#      target_z=target_z+value
#      print(param_set("TANKER_DEL_Z", target_z ,args.mavros_ns))
#     except KeyboardInterrupt:
#      raise

def main():
    parser = argparse.ArgumentParser(description="Commad line tool for getting, setting, parameters from MAVLink device.")
    parser.add_argument('-n', '--mavros-ns', help="ROS node namespace", default="/mavros")
    parser.add_argument('-v', '--verbose', action='store_true', help="verbose output")
    subarg = parser.add_subparsers()

    load_args = subarg.add_parser('load', help="load parameters from file")
    load_args.set_defaults(func=do_load)
    load_args.add_argument('file', type=argparse.FileType('rb'), help="input file")
    load_format = load_args.add_mutually_exclusive_group()
    load_format.add_argument('-mp', '--mission-planner', action="store_true", help="Select MissionPlanner param file format")
    load_format.add_argument('-qgc', '--qgroundcontrol', action="store_true", help="Select QGroundControl param file format")

    dump_args = subarg.add_parser('dump', help="dump parameters to file")
    dump_args.set_defaults(func=do_dump)
    dump_args.add_argument('file', type=argparse.FileType('wb'), help="output file")
    dump_args.add_argument('-f', '--force', action="store_true", help="Force pull params from FCU, not cache.")
    dump_format = dump_args.add_mutually_exclusive_group()
    dump_format.add_argument('-mp', '--mission-planner', action="store_true", help="Select MissionPlanner param file format")
    dump_format.add_argument('-qgc', '--qgroundcontrol', action="store_true", help="Select QGroundControl param file format")

    get_args = subarg.add_parser('get', help="get parameter")
    get_args.set_defaults(func=do_get)
    get_args.add_argument('param_id', help="Parameter ID string")

    set_args = subarg.add_parser('set', help="set parameter")
    set_args.set_defaults(func=do_set)
    set_args.add_argument('param_id', help="Parameter ID string")
    set_args.add_argument('value', help="new value")


    start_args = subarg.add_parser('start', help="start mission")
    start_args.set_defaults(func=do_start)
    start_args.add_argument('delta_z', help="delta/time")

    args = parser.parse_args(rospy.myargv(argv=sys.argv)[1:])
    args.func(args)


if __name__ == '__main__':
    main()

