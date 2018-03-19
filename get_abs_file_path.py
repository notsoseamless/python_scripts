#! /usr/bin/env python
'''
Test absolute file paths from file path list
John Oldman 31/05/2013
'''

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
version         = 'GET_ABS_FILE_PATH 1.0  30-10-2013'
logger          = ''
log_path        = 'c:\\oldman\\log\\get_abs_file_path.log'
in_file_name    = ''
out_file_name   = ''
IN_FILE_PTR     = ''
OUT_FILE_PTR    = ''
progress_disp   = 0



def panic():
    logger.error('panic')
    print('ERROR: check log file at ' + log_path)
    sys.exit()
    

def usage();
    print(version)
    print('Simple script to run cleartool command describe command')
    print('on paths in the in_file_name. Results are placed in the')
    print('out file.)
    print('USAGE: get_abs_file_path <in file_name> <out file name>')


def get_inputs():
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
    logger.info('processing')
    print('processing')
    for line in IN_FILE_PTR :
        result = execute_cmd('cleartool describe -short ' + line)
        # write line to out file
        OUT_FILE_PTR.write(result)
        display_progress()


def main():
    set_logger()
    print(version)
    logger.info(version)
    logger.info('begin')
    get_inputs()
    open_files()
    process_file()
    close files()
    logger.info('end')


if __name__ == '__main__':
   main()

# end

