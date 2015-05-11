#! /usr/bin/env python
'''

Script to identify uninitialised global variables.

Uses ctags for initial parse of c modules.

Outputs a text file with comer seperated fields:
    FILE, GLOBAL, INIT FUNCTION, COMMENTS
    text file defaults to 'uninit_globals.txt', can be changed.

Assumptions:
    Classification of init functions:
    Function names ending with _Init, _init, _initialize or _initStubData

    Classification of globals:
    ignoring variables and initialisations in #if constructs
    ignoring variables that end with an upper case letter (APV, APT etc)
    ignoring variables ending with '_padding_32_nvv'

'''

from __future__ import print_function
import argparse
import sys
import re
import subprocess


#globals
CONF_FILE = 'config.py'
verbose = False

def main():
    '''main function'''
    global verbose
    outfile_name = ''

    parser = argparse.ArgumentParser(
    description=__doc__,
    epilog=''
    )
    parser.add_argument('-o', help='specify results file name',
                        action='store',
                        dest='name')
    parser.add_argument('-v', help='verbose mode',
                        action='store_true',
                        dest='verbose')
    args = parser.parse_args()

    if args.name:
        # Use specified output file
        outfile_name = args.name
    else:
        outfile_name = 'uninit_globals.txt'

    if args.verbose:
        verbose = True

    # check if in working directory
    pwv = subprocess.Popen(['cleartool', 'pwv', '-s'],
          stdout=subprocess.PIPE).communicate()[0].rstrip()
    if re.match(r'\*\* NONE \*\*', pwv):
        print('Not in a ClearCase view - try running in a view from ./6_coding',
              file=sys.stderr)
        sys.exit(1)

    src_list = get_src_lst()
    if verbose:
        print(src_list)

    print('\nProcessing, may take some time...\n')

    # header
    results = []
    results.append('FILE, GLOBAL, INIT FUNCTION, COMMENTS\n')

    for file_name in src_list:
        if verbose:
            print('\nprocessing ' + file_name)
        var_list = get_globals(file_name)
        func_names = init_function_name(file_name)
        if not var_list:
            if not func_names:
                results.append(file_name + ',,,No globals or init function\n')
            else:
                results.append(file_name + ',,,No globals\n')
                read_init_function(file_name, func_names, var_list, results)
        else:
            if not func_names:
                results.append(file_name + ',,,No init function\n')
            read_init_function(file_name, func_names, var_list, results)


    results_to_file(results, outfile_name)

    if verbose:
        for lines in results:
            print(lines)



def results_to_file(results, outfile):
    '''output the results list to a file'''
    file_ptr = ''
    try:
        file_ptr = open(outfile, 'w')
    except IOError:
        print('failed to open ' + outfile)
        sys.exit()
    for line in results:
        file_ptr.write(line)
    print('Results in ' + outfile)
    file_ptr.close()



def get_src_lst():
    ''' get source file names and paths from the config.sys file '''
    file_ptr = ''
    source_file_list = []
    try:
        file_ptr = open(CONF_FILE, 'r')
    except IOError:
        print('failed to open ' + CONF_FILE)
        sys.exit()
    for line in file_ptr:
        commented_out = re.match(r' *#.*', line)
        if commented_out:
            pass
        else:
            # filter out those file names
            regex1 = re.compile('^SourceFile')
            regex2 = re.compile('\'')
            # load files into list
            if regex1.match(line):
                source_file_list.append(regex2.split(line)[1])
    file_ptr.close()
    return source_file_list



def init_function_name(file_name):
    ''' return init function name '''
    func_name = ''
    func_names = []
    if verbose:
        print(file_name + ' functions:')
    # tag functions
    cmd = "ctags -x --sort=yes --c-kinds=f --if0=no --file-scope=no "\
           + file_name
    ctag_functions_list = subprocess.check_output(cmd, stdin=None,
                                                  stderr=None, shell=True)
    regex_split = re.compile('function')
    regex_include = re.compile('_Init$|_init$|_initialize$|_initStubData$')
    for line in ctag_functions_list.splitlines():
        func_name = regex_split.split(line.strip())[0]
        func_name = re.sub(r'\s+$', '', func_name)    # remove eol white space
        if regex_include.search(func_name):
            func_names.append(func_name)
            if verbose:
                print('Listing function: ' + func_name)
    return func_names



def get_globals(file_name):
    ''' returns global variable names in c file '''
    vlist = []
    if verbose:
        print(file_name + ' globals:')
    # tag variables
    cmd = "ctags -x --sort=yes --c-kinds=v --if0=no --file-scope=no "\
           + file_name
    ctag_globals_list = subprocess.check_output(cmd, stdin=None,
                                                stderr=None, shell=True)
    regex_split = re.compile('variable')
    #regex_exclude = re.compile('^CONST|_APV$|_APM$|_APT$|_CPV$|_BPX$|_BPY$|_DAT$|_FLT_CFG$|_CONFIG_DATA$') # unwanted types
    regex_exclude = re.compile('^CONST|[A-Z]$|_padding_32_nvv$')
    for line in ctag_globals_list.splitlines():
        var = regex_split.split(line.strip())[0]
        var = re.sub(r'\s+$', '', var) # remove eol white space
        if not regex_exclude.search(var):
            vlist.append(var)
            if verbose:
                print('Listing global: ' + var)
    return vlist


def read_init_function(file_name, func_names, globals_list, results):
    ''' search init function for globals '''
    file_ptr = ''
    try:
        file_ptr = open(file_name, 'rU')
    except IOError:
        print('failed to open ' + file_name)
        sys.exit()
    #tgtfile = open(tgt,'w')
    contents_str = file_ptr.read()
    contents = contents_str.splitlines()
    contents = strip_comments(contents)
    file_ptr.close()

    # create a tempoary list copy for iterating
    temp_globals_list = list(globals_list)

    for func_name in func_names:
        if verbose:
            print('searching for function: ' + func_name)
        init_func = get_function(contents, func_name)
        if init_func:
            for global_var in temp_globals_list:
                if verbose:
                    print('searching for global: ' + global_var)
                if any(global_var in s for s in init_func):
                    results.append(file_name + ',' + global_var + ','
                                   + func_name + ',OK\n')
                    # remove from list so we do not check
                    # against the next init function
                    if global_var in globals_list:
                        globals_list.remove(global_var)
        else:
            results.append(file_name + ',' + func_name
                           + ',,function not found\n')

    # any globals left in the list imay not be initialised
    for global_var in globals_list:
        results.append(file_name + ',' + global_var
                           + ',,global not initialised\n')


def strip_comments(contents):
    ''' return a c module with the comments removed '''
    line_no = 0
    c_comment_count = 0
    for line in contents:
        # Strip out simple C++ comments from found point to end of line
        contents[line_no] = re.sub(r'//.*$', '', contents[line_no])
        if c_comment_count == 0:
            # currently not processing a multiline comment can strip out
            # one liner C comments
            contents[line_no] = re.sub(r'\/\*.*?\*\/', '', contents[line_no])
        else:
            if re.match(r'.*\*\/', contents[line_no]):
                # multiline comment ending on this line
                c_comment_count = 0
                contents[line_no] = re.sub(r'.*\*\/', '', contents[line_no])
            else:
                # whole line is a comment
                contents[line_no] = ''
        # search for a starting C comment but no finishing
        # C comment on this line
        if re.match(r'.*\/\*.*', contents[line_no]):
            if re.match(r'.*\*\/', contents[line_no]):
                pass
            else:
                # No comment termination found
                c_comment_count = c_comment_count + 1
                contents[line_no] = re.sub(r'\/\*.*', '', contents[line_no])
        line_no = line_no + 1
    return contents


def get_function(c_module, func_name):
    ''' return a named function from a c module '''
    func = []
    brace_count = 0
    in_func = False
    regex_func_name = re.compile(func_name + r'\(void\)')
    regex_open_brace = re.compile(r'\{')
    regex_close_brace = re.compile(r'\}')
    for line in c_module:
        if regex_func_name.search(line):
            in_func = True
            if verbose:
                print('found function: ' + func_name)
        if True == in_func:
            line = re.sub(r'\s+$', '', line)    # remove eol white spac
            # split trailing '=' and '[' from global names
            line = line.replace('[', ' [') # insert space
            line = line.replace('=', ' =') # insert space
            func.append(line)
            # search for function body braces
            if regex_open_brace.search(line):
                brace_count = brace_count + 1
            if regex_close_brace.search(line):
                brace_count = brace_count - 1
                if 0 == brace_count:
                    # reached end of function
                    return func


if __name__ == "__main__":
    main()


