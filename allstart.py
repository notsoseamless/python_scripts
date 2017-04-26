#! /usr/bin/env python
#######################################################################
#
# Description: Script makes start up faster
#
#              John Oldman 09/01/2014
#
########################################################################
# DATE       # DESCRIPTION                                       # WHO #
#------------#---------------------------------------------------#-----#
# 31-05-2013 # Initial version                                   # JRO #
# 15-10-2013 # Add logging:                                      #     #
#            # http://docs.python.org/2/howto/logging.html       # JRO #
#            #                                                   #     #
#            #                                                   #     #
#            #                                                   #     #
#            #                                                   #     #
########################################################################
#
# todo:
# fix logging
# fix threading
# add timer
#
########################################################################
import sys
import os
import time
import logging
import time
#import thread

version = 'allstart    1.3    09-01-2014'


no_of_args = len(sys.argv)
if no_of_args == 1 :
    print("usage: allstart <cr_number> [cr_description]")
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
log_path       = 'c:\\oldman\\log\\allstart.log'


def set_logger():
    global logger
    logger = logging.getLogger(log_path)
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(log_path)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def set_up_dirs():
    logging.info('set directories')
    global base_dir
    global root_dir
    global cr_description
    global template_dir
    global si_dir
    if no_of_args > 2 :
        cr_description = str(sys.argv[2])
    root_dir         = 'm:\\task_oldmanj_gv' + cr_number + '\\gill_vob\\6_coding'
    base_dir         = 'C:\oldman\CRs\Projects\GV00' + cr_number + "_" + cr_description
    build_dir        = base_dir + '\\build'
    visu_dir         = base_dir + '\\visu'
    visu_archive_dir = base_dir + '\\visu_archive'
    si_dir           = base_dir + '\\si'
    metrics_dir      = base_dir + '\\metrics'
    spec_dir         = base_dir + '\\specs'
    template_dir     = 'C:\\oldman\\CRs\\templates'  
    os.system('mkdir ' + base_dir)
    os.system('mkdir ' + build_dir)
    os.system('mkdir ' + visu_dir)
    os.system('mkdir ' + visu_archive_dir)
    os.system('mkdir ' + si_dir)
    os.system('mkdir ' + metrics_dir)
    os.system('mkdir ' + spec_dir)


def set_up_templates():
    logging.info('set up templates')
    os.system('copy ' + template_dir + '\\blank_resolution.zip ' +  base_dir + '\\gv' + cr_number + '_notes.zip')   
    os.system('copy ' + template_dir + '\\blank_Integration.xlsx ' +  base_dir + '\\gv' + cr_number + '_notes.xlsx')    
    os.system('copy ' + template_dir + '\\blank_notes.txt ' +  base_dir + '\\gv' + cr_number + '_notes.txt')
    os.system('copy ' + template_dir + '\\build_gv.bat '+ root_dir + '\\build_gv.bat')


def find_t55_duplicates():
    logging.info('t55 duplicate checker')
    os.system('copy ' + template_dir + '\\list_t55_duplicates.pl ' +  root_dir + '\\list_t55_duplicates.pl')
    os.system("perl " + root_dir + "\\list_t55_duplicates.pl")


def generate_file_list():
    global root_dir
    global template_dir
    global cr_number
    global si_dir
    logging.info('generate file list')
    os.chdir('m:')
    os.chdir(root_dir)
    qac       = '\\qac_test.pl'
    generator = '\\TCG_File_List_Generator_V2.0.pl'
    generated = '\\Generated_File_list.txt'
    os.system('copy ' + template_dir + qac + ' ' + root_dir + qac)
    os.system('copy ' + template_dir + generator + ' ' + root_dir + generator)
    os.system('perl ' +  root_dir + generator)
    os.system('del ' +  root_dir + generator)
    os.system('copy ' + root_dir + generated + ' ' + si_dir + generated)
    os.system('del ' + root_dir + generated)



def main():
    print ("Start Time : %s" %(time.ctime(time.time())))
    set_logger()
    print(version)
    logging.info('Started')
    logging.info('Get input')
    logging.info('call tstart')
    os.system("tstart " + cr_number)
    logging.info('set up local machine')
    set_up_dirs()
    set_up_templates()
    logging.info('build the code')
    os.chdir("m:")
    os.chdir(root_dir)
    os.system("build -j 8 GEN_QAC=NO > gv_build.log 2>&1")
    find_t55_duplicates()
    generate_file_list()
    logging.info('Finished')
    print ("End Time : %s" %(time.ctime(time.time())))


if __name__ == '__main__':
    main()



