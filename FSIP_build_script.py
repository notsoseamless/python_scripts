'''
Created on 4 Jul 2011

@author: zz0z07
'''

import os
import re
import shutil
import sys

# Root Directory pointing to null 
ROOT_DIR = ''

#Output file
OUTPUT_FILE_PATH = 'gill_vob\\6_coding\\base_sw\\fsip\\ecu_supplier\\o\\complete_file_list.lis'

#Path to append before object file 
Path_For_Dot_o = "..\..\..\\base_sw\\fsip\ecu_supplier\o\\"
Path_For_Dot_a = "..\..\..\\base_sw\\fsip\libs\\"
Path_For_Dot_elf = "..\..\..\pi_sup\elf\\"
New_elf_Name = "pi_sup.elf\n"

#===============================================================================
# The input file (FileToModify)is modified by appending 
# the given path (PathToAppend) and wrties to a new file (ModifiedFileOut) 
#===============================================================================
def ModifyPaths(FileToModify, ModifiedFileOut):
    
    try:
        InFile = open(FileToModify+'lnkobj_gcc.lis', 'r+')
    except IOError:
        print '\n[ !! ERROR !! ] : ', 'No such file or directory: ', FileToModify + 'lnkobj_gcc.lis'
        print '\n... Python script Terminated unexpectedly ....'
        sys.exit()
        
    OutFile = open(ModifiedFileOut, 'w')
    
    for line in InFile:
        val = re.sub(r'(.*\/)', r'', line)
        if(val != line):
            val1 = re.sub(r'(\w+\.)', r'', val)
            if val1 == "o\n":
                OutFile.write(Path_For_Dot_o + val)
            elif val1 == "a\n":
                OutFile.write(Path_For_Dot_a + val)
            elif val1 == "elf\n":
                if re.sub(r'(\.elf\n)', r'', val) == "c_i_external":
                    OutFile.write(Path_For_Dot_elf + New_elf_Name)
                else:       
                    OutFile.write(Path_For_Dot_elf + val)
        else:
            OutFile.write(val)

    InFile.close()
    OutFile.close()

#===============================================================================
# List all the files recursively based on the given file type(filepattern) 
# in a give Directory (rootdir)
#===============================================================================
def ListAllFiles(filepattern, rootdir):
    all_files = []
    for root, subdirs, files in os.walk(rootdir):
        for file in files:
            f = re.match(filepattern, file)
            if (f != None):
                all_files.append(os.path.join(root,file))
    return all_files

#===============================================================================
# List all object files and copy to dst directory using batch command
# THis is specific for copying search all object files and copy to dst directory
#===============================================================================
def CopyFiles_Via_Batch_Cmd(dst):
    print '\n\nListing all the object files and copying into objs.txt ... takes some time...'
    cmd = 'dir ' + ROOT_DIR + 'gill_vob\\6_coding\\src\\*.o /s/b > ' + ROOT_DIR + 'gill_vob\\6_coding\\objs.txt'    
    t = os.system(cmd)
    if(t == 0):
        f = open(ROOT_DIR + 'gill_vob\\6_coding\\objs.txt', 'r+')
        print '\n\nCopying all Object files to : ', ROOT_DIR + 'gill_vob\\6_coding\\base_sw\\fsip\\ecu_supplier\\o\\', '...takes few minutes depending on network traffic..'
        for line in f:
            CopyFile(line.rstrip(), dst)
            print '.',
        f.close()
        os.remove(ROOT_DIR + 'gill_vob\\6_coding\\objs.txt')
    else:
        print 'Could not execute system command :', '\ncmd'
        sys.exit()
        
#===============================================================================
# Delete all files in Destination root directory based on file-pattern
#===============================================================================
def DelAllFiles(filepattern, rootdir):
    files = ListAllFiles(filepattern, rootdir)
    for i in files:
        os.chmod(i, 0666)
        os.remove(i)

#===============================================================================
# Copy file from src to dst directory
#===============================================================================
def CopyFile(src, dst):
    if (os.path.isfile(src)):
        try:
            shutil.copy(src, dst)                
        except IOError as (errno, strerror):
            print "I/O error({0}): {1}".format(errno, strerror)
            print 'Could not copy File', src       
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise
    else:
        print '\n[ !! ERROR !! ] : ', 'File : ', 'Does not exist', src  
        pass

#===============================================================================
# Copy file from src to dst directory using system command
#===============================================================================
def CopyFIle_Via_System(src, dst):
    if (os.path.isfile(dst)):
        os.remove(dst)

    if (os.path.isfile(src)):
        cmd = 'copy ' + src + ' ' + dst
        os.system(cmd)
    else:
        print '\n[ !! ERROR !! ] : ', 'File : Does not exist', src
        print 'This file ', src, 'is needed to succeed this script. Please check and re-run !!'  
        print '\n... Python script Terminated unexpectedly ....'
        sys.exit()
        
#===============================================================================
# Copy all files from ROOT_DIR to Destination file directory based on file-pattern
#===============================================================================
def ListAndCopyFiles(filepattern, rootdir, dst):
    files = ListAllFiles(filepattern, rootdir)
    for i in files:
        CopyFile(i, dst)
        os.chmod(i, 0666)



#===============================================================================
# __main__ Function
#===============================================================================
if __name__ == '__main__':
    print '########################################################################'
    print '\n  This Python script requires      : 2.7.2 version Python Interpreter'
    print '  The Verion of this Script is     : V-1.0 '
    print '  The latest Date script modified  : 06th July 2011'
    print '\n#######################################################################\n'
        
    if (len(sys.argv) > 1):
        DIR = 'M:\\' + str(sys.argv[1]) + '\\'
        if (os.path.exists(DIR) == False):
            print '\n[ !! ERROR !! ] :No such ROOT Directory: ', DIR                      
            print '\nPlease give the correct View Name to python script: \neg: modify_paths.py [ VIEW_NAME ]'
            print '\n... Python script Terminated unexpectedly ....'
            sys.exit()            
        else:
            ROOT_DIR = DIR    
    else:
        print 'View Name is not given in the argument. \nTaking Default ROOT DIR :', ROOT_DIR, '...\n'
        if (os.path.exists(ROOT_DIR) == False):
            print '\n[ !! ERROR !! ] :No such ROOT Directory: ', ROOT_DIR                      
            print '\nPlease give the correct View Name to python script: \neg: modify_paths.py [ VIEW_NAME ]'
            print '\n... Python script Terminated unexpectedly ....'
            sys.exit()
            
    if(os.path.exists(ROOT_DIR + 'gill_vob') == False):
        print '\n[ !! ERROR !! ] : ' + ROOT_DIR + 'gill_vob Not found !!'                       
        print 'Please Mount gill_vob in your view directory ', ROOT_DIR
        print '\n... Python script Terminated unexpectedly ....'
        sys.exit()
    elif(os.path.exists(ROOT_DIR + 'blois_soft_vob') == False):
        print '\n[ !! ERROR !! ] : ' + ROOT_DIR + 'blois_soft_vob Not found !!'                       
        print 'Please Mount blois_soft_vob in your view directory ', ROOT_DIR
        print '\n... Python script Terminated unexpectedly ....'
        sys.exit()
    elif(os.path.exists(ROOT_DIR + 'tcg_cots_tool_vob') == False):
        print '\n[ !! ERROR !! ] : ' + ROOT_DIR + 'tcg_cots_tool_vob Not found !!'                       
        print 'Please Mount tcg_cots_tool_vob in your view directory ', ROOT_DIR
        print '\n... Python script Terminated unexpectedly ....'
        sys.exit()
    else:
        pass
            
       
    print '\nModifying path names to : ' + ROOT_DIR + 'gill_vob\\6_coding\\lnkobj_gcc.lis ....'
    ModifyPaths(ROOT_DIR + 'gill_vob\\6_coding\\', ROOT_DIR + OUTPUT_FILE_PATH)
    
    # Delete all object files
    #print '\n\nDeleting all existing object files in : ', ROOT_DIR + 'gill_vob\\6_coding\\base_sw\\fsip\\ecu_supplier\\o\\'
    #DelAllFiles('.*\.o', ROOT_DIR + 'gill_vob\\6_coding\\base_sw\\fsip\\ecu_supplier\\o\\')
 
    # List all object files from ROOT_DIR and copy to destination object directory
    CopyFiles_Via_Batch_Cmd(ROOT_DIR + 'gill_vob\\6_coding\\base_sw\\fsip\\ecu_supplier\\o\\')
    
    # List all object files from dest obj directory and copy to sub object file
    obj_files = ListAllFiles('.*\.o$', ROOT_DIR + 'gill_vob\\6_coding\\base_sw\\fsip\\ecu_supplier\\o\\')
    so_file = open(ROOT_DIR + 'gill_vob\\6_coding\\base_sw\\fsip\\sub_objects_list\\sub_objects.txt', 'w') 
    for i in obj_files:
        f = re.sub(r'(.*\\)', r'', i)
        so_file.write(f+'\n')
    so_file.close()
  
    # Delete all txt files in dest obj directory
    DelAllFiles('.*\.txt$', ROOT_DIR + 'gill_vob\\6_coding\\base_sw\\fsip\\ecu_supplier\\o\\') 
    DelAllFiles('.*\.txt$', ROOT_DIR + 'gill_vob\\6_coding\\base_sw\\fsip\\tools\\') 
    DelAllFiles('.*\.txt$', ROOT_DIR + 'gill_vob\\6_coding\\pi_sw\\build\\') 
	
    
    #COpy file from src to dst directory 
    CopyFIle_Via_System(ROOT_DIR + 'gill_vob\\6_coding\\src\\hwi\\hwi_core\\src\\hwi_memory_map.lsl', ROOT_DIR + 'gill_vob\\6_coding\\base_sw\\fsip\\lcf\\base_sw_loc_des_pp.opt')
    CopyFIle_Via_System(ROOT_DIR + 'gill_vob\\6_coding\\src\\appli\\c_i\\src\\c_i_external_adl.h', ROOT_DIR + 'gill_vob\\6_coding\\base_sw\\fsip\\lcf\\pi_sw_external_adl.h')
    
    DelAllFiles('.*\.txt$', ROOT_DIR + 'gill_vob\\6_coding\\base_sw\\fsip\\lcf\\')
    CopyFIle_Via_System(ROOT_DIR + 'gill_vob\\6_coding\\src\\appli\\c_i\\out\\c_i_external.elf', ROOT_DIR + 'gill_vob\\6_coding\\base_sw\\fsip\\super_plugin\\rb_plugin.a')
    DelAllFiles('.*\.txt$', ROOT_DIR + 'gill_vob\\6_coding\\base_sw\\fsip\\super_plugin\\')
    CopyFIle_Via_System(ROOT_DIR + 'gill_vob\\6_coding\\src\\appli\\c_i\\out\\c_i_external.elf', ROOT_DIR + 'gill_vob\\6_coding\\pi_sup\\elf\\pi_sup.elf')
    DelAllFiles('.*\.txt$', ROOT_DIR + 'gill_vob\\6_coding\\pi_sup\\elf\\')
    CopyFIle_Via_System(ROOT_DIR + 'gill_vob\\6_coding\\src\\hwi\\hwi_autosar\\lib\\hwi_autosar.a', ROOT_DIR + 'gill_vob\\6_coding\\base_sw\\fsip\\libs')
    CopyFIle_Via_System(ROOT_DIR + 'gill_vob\\6_coding\\src\\hwi\\hwi_pcp\\lib\\hwi_pcp.a', ROOT_DIR + 'gill_vob\\6_coding\\base_sw\\fsip\\libs')
    CopyFIle_Via_System(ROOT_DIR + 'ldcr_tools\\Osek\\Rta\\TRIHIGH\\Lib\\rtk_e.a', ROOT_DIR + 'gill_vob\\6_coding\\base_sw\\fsip\\libs')
    CopyFIle_Via_System(ROOT_DIR + 'gill_vob\\6_coding\\src\\appli\\c_i\\src\\libvolcano5.a', ROOT_DIR + 'gill_vob\\6_coding\\base_sw\\fsip\\libs')
    CopyFIle_Via_System(ROOT_DIR + 'gill_vob\\6_coding\\src\\s_s\\s_s_lib\\out\\s_s_lib.a', ROOT_DIR + 'gill_vob\\6_coding\\base_sw\\fsip\\libs')
    DelAllFiles('.*\.txt$', ROOT_DIR + 'gill_vob\\6_coding\\base_sw\\fsip\\libs')
    CopyFIle_Via_System(ROOT_DIR + 'gill_vob\\6_coding\\src\\appli\\c_i\\out\\c_i_external.a2l', ROOT_DIR + 'gill_vob\\6_coding\\pi_sw\\build\\pi_sw_external.a2l')
    CopyFIle_Via_System(ROOT_DIR + 'gill_vob\\6_coding\\'+ str(sys.argv[1]) +'_ATI.a2l', ROOT_DIR + 'gill_vob\\6_coding\\pi_sw\\build\\pi_sw.a2l')
    CopyFIle_Via_System(ROOT_DIR + 'gill_vob\\6_coding\\'+ str(sys.argv[1]) +'_VISU.a2l', ROOT_DIR + 'gill_vob\\6_coding\\pi_sw\\build\\pi_sw_delphi.a2l')
    CopyFIle_Via_System(ROOT_DIR + 'blois_soft_vob\\Software\\Environnement\\exe\\S3_To_S3_Flashable.pl', ROOT_DIR + 'gill_vob\\6_coding\\base_sw\\fsip\\tools\\S3_To_S3_Flashable.pl')
    CopyFIle_Via_System(ROOT_DIR + 'blois_soft_vob\\Software\\Environnement\\exe\\int2ulp.exe', ROOT_DIR + 'gill_vob\\6_coding\\base_sw\\fsip\\tools\\int2ulp.exe')
    CopyFIle_Via_System(ROOT_DIR + 'blois_soft_vob\\Software\\Environnement\\exe\\int2ulp.rsp', ROOT_DIR + 'gill_vob\\6_coding\\base_sw\\fsip\\tools\\int2ulp.rsp')
    CopyFIle_Via_System(ROOT_DIR + 'tcg_cots_tool_vob\\gnu\\srec_cat.exe', ROOT_DIR + 'gill_vob\\6_coding\\base_sw\\fsip\\tools\\srec_cat.exe')
    CopyFIle_Via_System(ROOT_DIR + 'tcg_cots_tool_vob\\gnu\\cygwin1.dll', ROOT_DIR + 'gill_vob\\6_coding\\base_sw\\fsip\\tools\\cygwin1.dll')                        
    
