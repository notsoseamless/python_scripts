#! /usr/bin/env python
''' 
Description: Script makes start up faster
John Oldman 05/02/2014
'''

import sys
import os
import time
import logging
import time
#import thread

version = 'allreview    0.1    05-02-2014'


no_of_args = len(sys.argv)
if no_of_args == 1 :
    print("usage: allreview <cr_number> [cr_description]")
    print("cr_description is optional")
if no_of_args > 1 :
    cr_number = str(sys.argv[1])


# globals
base_dir       = ''
cr_description = ''
root_dir       = ''
si_dir         = ''
template_dir   = ''
logger         = ''
log_path       = 'c:\\oldman\\log\\allreview.log'


def set_logger():
    global logger
    logger = logging.getLogger(log_path)
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(log_path)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def set_up_review_dirs():
    logging.info('set directories')
    global base_dir
    global cr_description
    global template_dir
    global si_dir
    global root_dir
    if no_of_args > 2 :
        cr_description = str(sys.argv[2])
    base_dir         = 'C:\\oldman\\CRs\\Projects\\GV00' + cr_number + "_review_" + cr_description
    si_dir           = base_dir + '\\si'
    spec_dir         = base_dir + '\\specs'
    template_dir     = 'C:\\oldman\\CRs\\templates'  
    os.system('mkdir ' + base_dir)
    os.system('mkdir ' + si_dir)
    os.system('mkdir ' + spec_dir)
    
def set_up_templates():
    logging.info('set up templates')
    os.system('copy ' + template_dir + '\\_Review.xls '+ base_dir + '\\' + 'gv' + cr_number + '_Review.xls')

def set_up_vob_files():
    global root_dir
    root_dir = str(sys.argv[3]) + '\\gill_vob\\6_coding'
    os.system('copy ' + template_dir + '\\qac_test.pl '+ root_dir + '\\qac_test.pl')
    duples = '\\list_t55_duplicates.pl '
    os.system('copy ' + template_dir + duples + root_dir + duples)
    os.chdir('m:')
    os.chdir(root_dir)
    os.system("perl " + root_dir + duples)
    generator = '\\TCG_File_List_Generator_V2.0.pl'
    generated = '\\Generated_File_list.txt'
    os.system('copy ' + template_dir + generator + ' ' + root_dir + generator)
    os.chdir('m:')
    os.chdir(root_dir)
    os.system('perl ' + root_dir + generator)
    os.system('del '  + root_dir + generator)
    os.system('copy ' + root_dir + generated + ' ' + si_dir + generated)


def main():
    global root_dir
    print ("Start Time : %s" %(time.ctime(time.time())))
    set_logger()
    print(version)
    logging.info('Started')
    logging.info('Get input')
    logging.info('set up local machine')
    set_up_review_dirs()
    set_up_templates()
    if no_of_args > 3 :
        set_up_vob_files()
        # need to work from vob from now
        os.chdir('m:')
        os.chdir(root_dir)
        os.system('find_tasks ' + cr_number)
    logging.info('Finished')
    print ("End Time : %s" %(time.ctime(time.time())))

if __name__ == '__main__':
    main()



