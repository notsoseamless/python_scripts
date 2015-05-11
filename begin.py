#! /usr/bin/env python
########################################################################
#                    Delphi Diesel Systems
#*
#*                   This document is the property of
#*                   Delphi Diesel Systems
#*                   It must not be copied (in whole or in part)
#*                   or disclosed without prior written consent
#*                   of the company. Any copies by any method
#*                   must also include a copy of this legend.
#######################################################################
#
# Description: Script makes start up faster
#
#              John Oldman 01/10/2013
#
########################################################################
# DATE       # DESCRIPTION                                       #     #
#------------#---------------------------------------------------#-----#
# 01-10-2013 # Initial version                                   # JRO #
#            #                                                   #     #
#            #                                                   #     #
#            #                                                   #     #
#            #                                                   #     #
#            #                                                   #     #
########################################################################
import sys
import os

print("\n\n\n\n\n");
print("BEGIN\n");
print("=====\n\n\n");


def os_caller(call_str):
	os.system(call_str);




###########################################################
# functions now defined
# start code
###########################################################

print('clearcase');
os_caller("clearexplorer.exe");

print('clearquest');
os_caller("clearquest.exe");

print('timesheet');
#os_caller("C:\\Documents and Settings\\tz2718\\oldman\\admin\\time.xls");

print('typing tutor');
#os_caller("C:\\Program Files\\Tipp10\\tipp10.exe");

print('memory');
os_caller("C:");
os_caller("cd C:\\oldman\\utils\\Memory");
#os_caller("C:\\oldman\\utils\\Memory\\MM.EXE");

print('task list');
#os_caller("vi C:\\Documents and Settings\\tz2718\\oldman\\admin\\note\\tech\\delphi_todo.txt");



