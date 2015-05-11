#!/usr/bin/env python
'''
go through project files looking for project branches from 
blois branches
'''

from __future__ import print_function
import argparse
import re
import sys
import os
import subprocess

def main():
    CLEARTOOL_CMD = 'cleartool'
    CLEARTOOL_SUB_CMD = 'ls'
    DEVNULL = open(os.devnull, 'w')
    try:
        __version__ = subprocess.Popen([CLEARTOOL_CMD, CLEARTOOL_SUB_CMD, __file__],
                                        stdout=subprocess.PIPE,
                                        stderr=DEVNULL).communicate()[0]
        if not __version__:
            __version__ = 'unknown'
    except:
        __version__ = 'unknown'
    print('Script version', __version__)

    configfile = 'config.py'
    configfile = open(configfile, 'r')

    # get file names from config file
    for line in configfile:
	if re.match(r'^HeaderFile|^SourceFile|^T55File', line):
	    line = re.sub('[\)\(]',',',line)
	    line = re.sub('[\'"]','',line)
	    line = re.split(',',line)
            file = line[1]
	    print(file)



    configfile.close()






if __name__ == '__main__':
    status = main()
    exit(status)

