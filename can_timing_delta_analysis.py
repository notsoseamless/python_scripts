#! /usr/bin/env python

'''
script to analyse canalyser output asc file
outputs a csv report file for each CAN Rx message

John Oldman

version 0.2  07-05-2015

'''


import time
import sys
import re
import subprocess
import getopt
import datetime
import math


#globals
VERBOSE = True
DEBUG = True
__VERSION__ = '0.2'



def main():
    ''' main function '''
    global VERBOSE, DEBUG

    # time module
    start = time.clock()

    can_data_file_name = ''

    # check any run arguments adn get the input file name
    if len(sys.argv) < 2:
        print '\n\nUsage: ' + sys.argv[0] + ' [can asc file]\n'
        sys.exit(2)
    else:
        can_data_file_name = sys.argv[1]

    # do the analysis
    analyse_can_messages(can_data_file_name)

    # report duration
    if VERBOSE:
        td = time.clock() - start
        print 'took %2.0f minutes, %2.0f seconds' %(td/60, td%60)




def get_can_data(file_name):
    ''' imports can data from canalyser asc file '''
    file_ptr = ''
    try:
        file_ptr = open(file_name, 'r')
    except IOError:
        print 'failed to open ' + file_name
        sys.exit()
    file_data = file_ptr.readlines()
    file_ptr.close()
    return file_data



class can_message():
    ''' represents a can message '''
    def __init__(self, id, can_data):
        self.id = id
        self.can_data = can_data
        self.min_dev = 0
        self.max_dev = 0

    def analyse_data(self):
        pass

    def calculate_devation_limits(self):
        pass

    def print_results():
        pass

    def calc_nom_period(self):
        ''' helper calculates the nominal period for a can message id '''
        msg_count = 0
        total_delta_time = 0
        previous_time = 0
        for line in self.can_data:
            line = line.strip()
            words = line.split()
            if len(words) > 4:
                if words[2] == self.id:
                    msg_count += 1
                    time = float(words[0])
                    total_delta_time += time - previous_time
                    previous_time = time
        self.nom_period = round(total_delta_time / msg_count, 3)




def analyse_can_messages(file_name):
    ''' core analysis function '''

    # get can data from canalyser file
    can_data = get_can_data(file_name)

    # list Rx messages in can_data
    msg_id_set = set([line.split()[2] for line in can_data if re.search('\\bRx\\b',line)])

    for id in msg_id_set:
        try:
            file_name = 'Can_message_' + id + '_data_analysis.csv'
            file_ptr = open(file_name, 'w')
        except IOError:
            print 'failed to open ' + file_name
            sys.exit()
        # set max deviation for message period
        nominal = calc_nom_period(id, can_data)
        previous_time = 0.0
        deviation = 0.2
        min = nominal - (nominal * 0.2)
        max = nominal + (nominal * 0.2)
        # put header in file
        now = datetime.datetime.now()
        file_ptr.write('Delphi Can Message Period Timing Delta Analysis Report\n')
        file_ptr.write('Generated ' + now.strftime('%Y-%m-%d %H:%M') + ' using ' +  sys.argv[0] + ' Version ' + __VERSION__ +'\n')
        file_ptr.write('Message ID ' + id + '\n')
        file_ptr.write('Nominal period: ' + str(nominal) + ' PASS Deviation = +/-' + str(deviation * 100) + '%\n' )
        file_ptr.write('time,,id,dir,' + 'data,'*10 + 'delta,OK\n')
        # analyse id timings
        first_sample = True  # first sample will not be valid
        fail_count = 0
        for line in can_data:
            line = line.strip()
            words = line.split()
            if len(words) > 4:
                if (words[2] == id) and (words[3] == 'Rx'):
                    time = float(words[0])
                    delta_time = time - previous_time
                    if not first_sample:
                        if (delta_time > min) and (delta_time < max):
                            result = 'PASS'
                        else:
                            result = 'FAIL'
                            fail_count += 1
                    else:
                        result = 'n/a'
                    first_sample = False
                    previous_time = time
                    line = line.split()             # make line into list
                    line.append(str(delta_time))    # add delta time to line
                    line.append(result)             # add result to line
                    outline = ','.join(line) + '\n' # csv format
                    file_ptr.write(outline)
        print 'Found ' + str(fail_count) + ' errors in message id ' + id
        file_ptr.close()




def calc_nom_period(id, can_data):
    ''' helper calculates the nominal period for a can message id '''
    msg_count = 0
    total_delta_time = 0
    previous_time = 0
    for line in can_data:
        line = line.strip()
        words = line.split()
        if (len(words) > 4) and (words[2] == id):
            msg_count += 1
            time = float(words[0])
            total_delta_time += time - previous_time
            previous_time = time

    #return set([line.split()[2] for line in can_data if regex_rx.search(line)])



    return round(total_delta_time / msg_count, 3)

       
    

if __name__ == '__main__':
    main()


