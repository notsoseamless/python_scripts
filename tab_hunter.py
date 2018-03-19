#! /usr/bin/env python
'''
Description: Script hunts and distroys tabs and eol spaces
John Oldman 24/10/2013
'''

import sys
import os
import subprocess
import time
import logging
import time
#import thread


# global names
version         = 'TAB HUNTER 1.0    25-10-2013'
logger          = ''
IN_FILE_PTR     = ''
OUT_FILE_PTR    = ''
in_file_name    = ''
out_file_name   = 'temp'
file_length     = 0
tab_lines       = 0
eol_space_lines = 0


no_of_args = len(sys.argv)
if no_of_args == 2 :
    in_file_name = str(sys.argv[1])
else :
    print('USAGE: tab_hunter <file_name>')
    sys.exit()


def panic():
    print('ERROR: check log file')
    sys.exit()


# generate a unique output file name
def get_out_file_name():
    global logger
    global in_file_name
    global out_file_name
    logger.info('generate out file name')
    suffix = 0; 
    out_file_name = in_file_name + '_update_%s' %(suffix)  
    while os.path.exists(out_file_name):
        suffix +=1
        out_file_name = in_file_name + '_update_%s' %(suffix)
    return out_file_name

       
def open_files():
    global logger
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
        OUT_FILE_PTR = open(get_out_file_name(), 'w')
        logger.info(out_file_name + ' opened')
    except IOError:
        logger.error('failed to open ' + out_file_name)
        panic()

       
def set_logger():
    global logger
    logger = logging.getLogger('c:\\oldman\\log\\tab_hunter.log')
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler('c:\\oldman\\log\\tab_hunter.log')
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def process_file():
    global in_file_name
    global file_length
    global IN_FILE_PTR
    global OUT_FILE_PTR
    logger.info('processing')
    for line in IN_FILE_PTR :
        # replace tabs
        line = line.replace('\t', '    ')
        # strip eol white spaces
        line = line.rstrip()
        file_length += 1
        # write line to out file
        OUT_FILE_PTR.write(line + '\n')


def report_results():
    logger.info('generate report')
    print('processed %s lines of ' %(file_length) + in_file_name)
#    print('%s lines with tabs, %s lines with eol spaces' %(tab_lines) %(eol_space_lines))
    print('results in ' + out_file_name)



def main():
    set_logger()
    print(version)
    logger.info(version)
    logger.info('begin')
    open_files()
    process_file()
    logger.info(in_file_name + ' closed')
    IN_FILE_PTR.close()
    logger.info(out_file_name + ' closed')
    OUT_FILE_PTR.close()
    report_results()
    logger.info('end')


if __name__ == '__main__' :
    main()


