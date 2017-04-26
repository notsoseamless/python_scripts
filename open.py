#!/usr/bin/env python
'''
    this runs in vob 6_coding
    looks for file name in config.py and opens it
'''

import time
import sys
import re
import subprocess
import getopt
import datetime
import os


#constants
CONF_FILE = 'config.py'



def main():
    ''' main function '''

    # time this module
    start = time.clock()

    # check that file name was provided
    file_name = ''
    if len(sys.argv) < 2:
        print 'ERROR: Need to enter a file name'
        sys.exit(1)
    else:
        file_name =  str(sys.argv[1])
        print 'Looking for', file_name

        # report version of this file
    print 'version',  shell_cmd('cleartool ls ' + __file__)

    # find view name
    pwv = shell_cmd('cleartool pwv -s')

    # check if in working directory
    if re.match(r'\*\* NONE \*\*', pwv):
        print 'Not in a ClearCase view - try running in a view from ./6_coding'
        sys.exit(1)

    


def get_file_path():
    ''' helper gets file path from config file '''
    # open the config file
    file_ptr = ''
    source_file_list = []
    try:
        file_ptr = open(CONF_FILE, 'r')
    except IOError:
        print 'failed to open ' + CONF_FILE
        sys.exit()
    for line in file_ptr:
        commented_out = re.match(r' *#.*', line)
        if commented_out:
            pass
        else:
            # filter out those file names
            regex_match = re.compile('^SourceFile')
            regex_split = re.compile('\'')
            # load files into list
            if regex_match.match(line):
                source_file_list.append(regex_split.split(line)[1])
    file_ptr.close()


def shell_cmd(cmd):
    ''' helper to run a shell command '''
    try:
        return subprocess.Popen(cmd, stdin=None,
                                stdout=subprocess.PIPE,
                                stderr=None, shell=True).communicate()[0].strip()
    except:
        return 'unknown'
        sys.exit(1)



if __name__ == "__main__":
    main()








