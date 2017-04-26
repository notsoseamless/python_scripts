#! /usr/bin/env python
#######################################################################
#
# Description: Script gets absolute file paths from file path list
#              and identifies autocoded files
#
#              John Oldman 31/05/2013
#
########################################################################
# DATE       # DESCRIPTION                                       # WHO #
#------------#---------------------------------------------------#-----#
# 31-10-2013 # Initial version                                   # JRO #
#            #                                                   #     #
#            #                                                   #     #
#            #                                                   #     #
#            #                                                   #     #
#            #                                                   #     #
#            #                                                   #     #
#            #                                                   #     #
#            #                                                   #     #
#            #                                                   #     #
#            #                                                   #     #
########################################################################
#
# todo:
#
#
#
#
#
########################################################################
import sys
import os
import re
import time
import logging
import time
from optparse import OptionParser
from subprocess import *
#import thread


# global names
version         = 'AUTOCODE HUNTER 1.0  31-10-2013'
logger          = ''
log_path        = 'c:\\oldman\\log\\autocode_hunter.log'
in_file_name    = ''
out_file_name   = ''
IN_FILE_PTR     = ''
OUT_FILE_PTR    = ''
C_FILE_PTR      = ''
progress_disp   = 0


def panic():
    logger.error('panic')
    sys.exit()
    

def usage():
    print(version)
    print('Simple script to go through file list identifying autocode files')
    print('USAGE: get_abs_file_path <in file_name> <out file name>')


def get_inputs():
    global in_file_name
    global out_file_name
    no_of_args = len(sys.argv)
    if no_of_args == 3 :
        in_file_name  = str(sys.argv[1])
        out_file_name = str(sys.argv[2])
    else :
        usage()
        sys.exit()
   

# Function to execute external dos commands.
def execute_cmd(cmd):
    p = Popen(cmd, shell=True, stdout=PIPE, stderr=STDOUT)
    result = p.communicate()[0]
    return result


def open_files():
    global logger
    global in_file_name
    global out_file_name
    global IN_FILE_PTR
    global OUT_FILE_PTR
    try:
        IN_FILE_PTR = open(in_file_name, 'r')
        logger.info(in_file_name + ' opened')
    except IOError:
        logger.error('failed to open ' + in_file_name)
        panic()
    try:
        OUT_FILE_PTR = open(out_file_name, 'w')
        logger.info(out_file_name + ' opened')
    except IOError:
        logger.error('failed to open ' + out_file_name)
        panic()  


def open_c_file(c_file_name):
    global logger
    global C_FILE_PTR
    execute_cmd('type c_file_name')
    try:
        C_FILE_PTR = open(c_file_name, 'rU')
        logger.debug(c_file_name + ' opened')
    except IOError:
        logger.error('failed to open ' + c_file_name)
        panic()


def close_files():
    logger.info(in_file_name + ' closed')
    IN_FILE_PTR.close()
    logger.info(out_file_name + ' closed')
    OUT_FILE_PTR.close()


def set_logger():
    global logger
    logger = logging.getLogger(log_path)
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(log_path)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def display_progress():
    global progress_disp
    if progress_disp == 0 :
       print '|\b\b' ,
       progress_disp +=1
    elif progress_disp == 1 :
       print '/\b\b' ,
       progress_disp +=1
    elif progress_disp == 2 :
       print '\\\b\b' ,
       progress_disp +=1
    elif progress_disp > 2 :
       print '_\b\b' ,
       progress_disp = 0
    else :
       pass


# parse each line of the in file, run a cleartool on it 
# and place results in out file
def process_file():
    global IN_FILE_PTR
    global OUT_FILE_PTR
    global C_FILE_PTR
    autocode_id     = 'Real-Time Workshop'
    logger.info('processing')
    print('processing')
    for line in IN_FILE_PTR :
        is_autocode_file = 0
        line = line.rstrip()
        open_c_file(line)
        for c_line in C_FILE_PTR :
            if ( -1 != c_line.find('Real-Time Workshop') ):
                is_autocode_file = 1
                break
        if (is_autocode_file > 0):
            OUT_FILE_PTR.write(line + '  ,  TCG_AUTOCODE\n' )
        else :
            OUT_FILE_PTR.write(line + '\n')
        C_FILE_PTR.close()
        display_progress()


def main():
    set_logger()
    print(version)
    logger.info(version)
    logger.info('begin')
    get_inputs()
    open_files()
    process_file()
    close_files()
    logger.info('end')


if __name__ == '__main__':
   main()

# end

