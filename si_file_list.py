#!/usr/bin/env python
'''

Script searches generates file list for SI

'''

import time
import sys
import re
import subprocess
import getopt
import datetime
import os

#globals
CONF_FILE = 'config.py'
FILE_LIST = 'si_file_list.txt'
verbose = False
debug = False




def main():
    ''' main function '''
    global verbose, debug, outfile_name

    # time this module
    start = time.clock()

    # report version of this file
    __version__ = shell_cmd('cleartool ls ' + __file__)

    # find view name
    pwv = shell_cmd('cleartool pwv -s')

    # check any run arguments
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hvo:d", ["help", "outfile="])
    except getopt.GetoptError, err:
        # print help information and exit:
        print str(err)
        print_help()
        sys.exit(2)
    for o, a in opts:
        if o in '-v':
            verbose = True
        elif o in ('-o', '--outfile'):
            # Use the output file specified
            FILE_LIST = a
                # do nothing
        elif o in ('-d', '--debug'):
            VERBOSE = True
            debug = True
        elif o in '-h':
            print_help()
            sys.exit(2)
        else:
            assert False, 'unhandled option'

    # check if in working directory
    if re.match(r'\*\* NONE \*\*', pwv):
        print 'Not in a ClearCase view - try running in a view from ./6_coding'
        sys.exit(1)

    print '\nProcessing, may take some time...\n'

    # list all src files
    src_list = get_src_list(pwv)

    # manual file list
    add_manual_files_to_list(pwv, src_list)

    # generate file list
    output_file_list(src_list)

    # report duration
    if verbose:
        td = time.clock() - start
        print 'took %2.0f minutes, %2.0f seconds' %(td/60, td%60)
        print '\n\n'




def shell_cmd(cmd):
    ''' run a shell command '''
    try:
        return subprocess.Popen(cmd, stdin=None,
                                stdout=subprocess.PIPE,
                                stderr=None, shell=True).communicate()[0].strip()
    except:
        return 'unknown'




def get_src_list(pwv):
    ''' gets source file names and paths from the config.sys file '''
    if verbose:
        print 'Generating list of source files'
    file_ptr = ''
    source_file_list = []
    try:
        file_ptr = open(CONF_FILE, 'r')
    except IOError:
        print 'failed to open ' + CONF_FILE
        sys.exit()
    for line in file_ptr:
        # make separators POSIX
        line = re.sub(r'\\', '/', line)
        commented_out = re.match(r' *#.*', line)
        if commented_out:
            pass
        else:
            # filter out those file names
            regex_search = re.compile('^SourceFile|^HeaderFile|^T55File|^ModelFile|^OtherFile|^OtherheaderFile|^xmlFile|^AsmFile|^ObjectFile')
            regex_split = re.compile(r'\'')
            if regex_search.match(line):
                raw_path = regex_split.split(line)[1]
                # three scenarios are considered:
                # (1) file in config.py is actual
                # (2) file is a symbolic link to a file another VOB with same name
                # (3) file is a symbolic link to a file in same directory with different name 
                # check if symbolic link
                cmd = 'cleartool describe -fmt "%[slink_text]Tp" ' + raw_path
                link_path = shell_cmd(cmd)
                if link_path:
                    # symbolic link
                    # make separators POSIX
                    link_path = re.sub(r'\\', '/', link_path)
                    # break path onto a list
                    temp_path = link_path.split('/')
                    if len(temp_path) == 1:
                        # link must be in same directory, remove file name from raw_path
                        short_path = remove_file_name(raw_path)
                        # append real file name
                        short_path = short_path + '/' + temp_path[0]
                        # complete the full path
                        full_path = 'm:/' + pwv + '/gill_vob/6_coding/' + short_path 
                    else:
                        # link probably in another VOB
                        # remove any '..'
                        cleaned_path = []
                        for path in temp_path:
                            if path != '..':
                                cleaned_path.append(path)
                        relative_path = '/'.join(cleaned_path)
                        full_path = 'm:/' + pwv + '/' + relative_path
                else:
                    full_path = 'm:/' + pwv + '/gill_vob/6_coding/' + raw_path
                source_file_list.append(full_path)
    file_ptr.close()
    if debug:
        print source_file_list
    return source_file_list




def remove_file_name(file_path):
    ''' helper returns file_path as a string with file name removed
        assumes file_path is a string
        assumes POSIX path '''
    file_path = file_path.split('/')
    file_path.pop()
    file_path = '/'.join(file_path)
    return file_path
    



def add_manual_files_to_list(pwv, src_list):
    ''' these files we manually add '''
    if verbose:
        print 'Merging manual listed files'
    pre_str = 'm:/' + pwv + '/'
    src_list.append(pre_str + 'gill_vob/6_coding/src/hwi/hwi_core/src/hwi_memory_map.lsl')
    src_list.append(pre_str + 'gill_vob/6_coding/config_ford_euro6.py')    
    src_list.append(pre_str + 'gill_vob/6_coding/build.bat')
    src_list.append(pre_str + 'blois_soft_vob/Software/S_S/s_s_scheduler/src/s_s_scheduler.pl')
    src_list.append(pre_str + 'gill_vob/6_coding/src/s_s/s_s_scheduler/src/tasklist_ford_euro6.asc')
    src_list.append(pre_str + 'gill_vob/6_coding/src/appli/c_i/c_i_vector/geny/src/GENy_vpb.gny')
    src_list.append(pre_str + 'gill_vob/6_coding/src/appli/c_i/c_i_vector/geny/src/GENy2_polling.gny')
    src_list.append(pre_str + 'gill_vob/6_coding/src/appli/c_i/c_i_vector/geny/src/GENy2_polling_interrupt.gny')
    src_list.append(pre_str + 'gill_vob/6_coding/src/appli/c_i/c_i_vector/geny/src/GENy2_Txpolling_Rxinterrupt.gny')
    src_list.append(pre_str + 'gill_vob/6_coding/src/appli/c_i/c_i_vector/geny/src/CD4_13_HS1_CGEA1_3_M10b_01d.dbc')
    src_list.append(pre_str + 'gill_vob/6_coding/src/appli/c_i/c_i_vector/geny/src/hthomas6_1111_CAN_VP09_Rel.dbc')
    src_list.append(pre_str + 'gill_vob/6_coding/src/appli/c_i/c_i_vector/geny/src/preconfig_pb_canlingw_hscan_DemoOnly')
    src_list.append(pre_str + 'gill_vob/6_coding/src/appli/c_i/out/c_i_external.a2l')
#    src_list.append(pre_str + 'gill_vob/6_coding/src/appli/_appli/src/application_stub_ford_euro6.c')
#    src_list.append(pre_str + 'gill_vob/6_coding/src/appli/_appli/src/application_ford_euro6application_ford_euro6.t55')
#    src_list.append(pre_str + 'gill_vob/6_coding/src/p_l/p_l_nvm/src/p_l_nvm_data_ford_euro6.c')
    return src_list




def output_file_list(src_list):
    ''' generate the output file from the src list '''
    if verbose:
        print 'Outputing to file'
    file_ptr = ''
    try:
        file_ptr = open(FILE_LIST, 'w')
    except IOError:
        print 'failed to open ' + FILE_LIST 
        sys.exit()
    for line in src_list:
        file_ptr.write(line + '\n')
        # report if file does not exist
        if not os.path.isfile(line):
            print 'ERROR: ' + line + ' does not exist'
    print 'File list in ' + FILE_LIST
    file_ptr.close()




def print_help():
    ''' help message '''
    print "Usage: si_file_list.py[OPTION][FILE_LIST]"
    print "Script to generate a file list for SI"
    print
    print "     -h, --help           print this help message"
    print "     -o, --outfile        specify file list name"
    print "     -v                   more detailed information"
    print




if __name__ == "__main__":
    main()



