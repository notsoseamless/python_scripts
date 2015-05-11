from subprocess import Popen, PIPE
from project import Setting, AsString
from project import sourceList, asmList, objectList
import logging
import re

logging.info("Setting target toolchain to " + __name__)

Setting(name = 'CPP', 
        replace = False,
        value = 'c:/gcc/esys/bin/powerpc-8540-eabi-cpp.exe')

Setting(name = 'CC', 
        replace = False,
        value = 'c:/gcc/esys/bin/powerpc-8540-eabi-gcc.exe')

Setting(name = 'CCCOM', 
        replace = False,
        value = '$NULL_EXIT $CC $CCFLAGS 2>&1 | $TEE ${TARGET.base}.err')

Setting(name = 'LINK', 
        replace = False,
        value = 'c:/gcc/esys/bin/powerpc-8540-eabi-ld.exe')

Setting(name = 'LINKCOM', 
        replace = False,
        value = '$LINK $LINKFLAGS')

Setting(name = 'AS', 
        replace = False,
        value = 'c:/gcc/esys/bin/powerpc-8540-eabi-as.exe')

Setting(name = 'ASCOM', 
        replace = False,
        value = '$AS $ASFLAGS')

Setting(name = 'CPPDEFPREFIX', 
        replace = False,
        value = '-D')

Setting(name = 'CPPAUTOINCPREFIX',
        replace = False,
        value = '-include ')

Setting(name = 'CPPAUTOINCSUFFIX',
        replace = False,
        value = '')

Setting(name = 'INCPREFIX', 
        replace = False,
        value = '-I')

Setting(name = 'CCFLAGS', 
        replace = False,
        value = AsString('''
 $_CPPINCFLAGS
 $_CPPDEFFLAGS
 $_CPPAUTOINC
 $USER_CCFLAGS
 -Os
 -g -g3 -gdwarf-2
 -fshort-enums
 -fno-unit-at-a-time
 -finline-functions-called-once
 -Wall
 -W
 -Wbad-function-cast
 -Wcast-align
 -Wmissing-declarations
 -Wmissing-prototypes
 -Wnested-externs
 -Wpointer-arith
 -Wredundant-decls
 -Wstrict-prototypes
 -fomit-frame-pointer
 -pipe 
 -o $TARGET
 -c
 ${TARGET.base}.c
'''))

Setting(name = 'LINKFLAGS', 
        replace = False,
        value = AsString('''
 -o ${TARGET.base}.elf
 --no-check-sections 
 --gc-sections 
 --warn-common
 -Map ${TARGET.base}.map
 -T lnkobj_gcc.lis
 -T src/blois_src/Hwi/src/hwi_memory_map.dld
 -L "$ROOT/tcg_cots_tool_vob/gnu_ppc/lib/gcc/powerpc-eabi/3.4.4"
 -lm -lc -lgcc
 --cref
'''))

Setting(name = 'LINK_DEPS',
        replace = False,
        value = 'src/blois_src/Hwi/src/hwi_memory_map.dld') 

def PreprocessFunction(target, source, env):
    """Preprocess Function for mpc555_gcc target
    
    This builder runs a preprocess operation to generate a .c file in the out directory
    It handles a variable number of injectors and also processes calibration items
    it puts attributes of the format :- FRED_APV __attribute__ ((section (".app_data"))) = ....;
    
    """
    log_str = "Generating target (for a mpc5554_gcc compiler) " + str(target[0]) + " from source " + str(source[0])
    logging.info(log_str)    
    src = str(source[0])
    tgt = str(target[0])   
    srcfile = open(src)
    tgtfile = open(tgt,'w')
    contents = srcfile.read()
      
    # Deal with modifying constant arrays to MAX injectors
    contents = re.sub(r'(\[\s*)APP_NUMBER_OF_INJECTORS_CPV(\s*\])',r'\1APP_MAX_NUMBER_OF_INJECTORS_CPV\2',contents)
    contents = contents.splitlines()
    
    # Find all legal APV bar ESM_ names which are declarations or externs
    pat_apvs = re.compile(r'([A-Z_]{3}|IN)(_[A-Z0-9_]+_)(APV|APT|DAT|DAT_\d+|BPX|BPY)$')
    pat_esm = re.compile(r'(ESM)(_[A-Z0-9_]+_)(APV|APT|DAT|DAT_\d+|BPX|BPY)$')    
    pat_const_cpv = re.compile(r'(CONST)(_\w+_)(CPV)$')
    p = Popen("ctags --language-force=c --sort=no -x --c-kinds=v " + src , stdout=PIPE)
    for line in p.stdout:
        tags = line.split()
        
        if pat_esm.match(tags[0]):
            current_line = contents[int(tags[2]) - 1]
            current_tag = tags[0]
            current_tag = pat_esm.sub(r'__attribute__ ((section (".esm_l2_appdata"))) \1\2\3', tags[0])
            pat_tag = re.compile(tags[0])
            contents[int(tags[2]) - 1] = pat_tag.sub(current_tag, current_line)
        elif pat_apvs.match(tags[0]):
            current_line = contents[int(tags[2]) - 1]
            current_tag = tags[0]
            current_tag = pat_apvs.sub(r'__attribute__ ((section (".app_data"))) \1\2\3', tags[0])
            pat_tag = re.compile(tags[0])
            contents[int(tags[2]) - 1] = pat_tag.sub(current_tag, current_line)
        elif pat_const_cpv.match(tags[0]):
            current_line = contents[int(tags[2]) - 1]
            current_tag = tags[0]
            current_tag = pat_const_cpv.sub(r'__attribute__ ((section (".app_data"))) \1\2\3', tags[0])
            pat_tag = re.compile(tags[0])
            contents[int(tags[2]) - 1] = pat_tag.sub(current_tag, current_line)
                    
    tgtfile.write("\n".join(contents))
    # write blank line in case source does not have one, keeps GCC from issuing warning
    tgtfile.write("\n")
    srcfile.close
    tgtfile.close
    return None

def LinkFunction(target, source, env, for_signature):
    """Link Function for an mpc5554_gcc target
    
    This builder runs a link operation
    
    """
    log_str = "Generating node target lnkobj_gcc.lis" + " from " + str(env['LINKLIST'])   
    logging.info(log_str)
    src = str(env['LINKLIST'])
    tgt = "lnkobj_gcc.lis"   
    srcfile = open(src)
    tgtfile = open(tgt,'w')
    tgtfile.write("INPUT(\n");
    for line in srcfile.readlines():
        line = line[:-1]
        tgtfile.write(line + "\n")
    tgtfile.write(")\n")
    srcfile.close
    tgtfile.close
    for file in source:
        logging.info(str(file))    
    return ('$LINKCOM')
    
def GenArchiveFunction(target, source, env):
    """Archive a set of files into a GNU library
    
    This is a default way of generating superobject files, for other processor families
    override this function in the processor.py file
    
    """
    log_str = "Generating archive node target " + str(target[0])
    logging.info(log_str)
    for file in source:
        logging.info(str(file))
    cmd = ""
    cmd_file = open(str(target[0]),'wU')
    for file in source:
        cmd = cmd + str(file) + "\n"
    cmd = re.sub(r'\\',r'/',cmd)
    cmd_file.write('INPUT(\n')
    cmd_file.write(cmd)
    cmd_file.write(')\n')
    return None
    
