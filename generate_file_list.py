#!/usr/bin/env python
'''

Script generates file list for source insight

'''

import time
import sys
import re
import subprocess
import getopt
import datetime

#globals/constants
CONF_FILE = 'config.py'
DEBUG = False
FILE_LIST_NAME = 'generated_file_list.txt'

def main():
    ''' main function '''
    global DEBUG, FILE_LIST_NAME

    # time this module
    start = time.clock()


    print '\nProcessing, will take some time ...\n'

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

    if DEBUG:
        print source_file_list

    list_to_file(source_file_list, FILE_LIST_NAME)


    td = time.clock() - start
    print 'took %2.0f minutes, %2.0f seconds' %(td/60, td%60)


def list_to_file(lst, outfile):
    ''' output the lst to a file
        assumes that lst is a list
        assumes that outfile is a filename string '''
    file_ptr = ''
    try:
        file_ptr = open(outfile, 'w')
    except IOError:
        print 'failed to open ' + outfile
        sys.exit()
    for line in lst:
        file_ptr.write(line)
    print 'results in ' + outfile
    file_ptr.close()


if __name__ == "__main__":
    main()



