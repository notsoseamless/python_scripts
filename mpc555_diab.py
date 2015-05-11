from subprocess import Popen, PIPE
from project import Setting, AsString
import logging
import re

logging.info("Setting target toolchain to " + __name__)

Setting(name = 'CPPFLAGS', 
        replace = False,
        value = AsString('''
 -E
 -D asm
 -WDDIABLIB=$ROOT/ldcr_tools/diab/5.0a
'''))

Setting(name = 'LIB_CCFLAGS', 
        replace = False,
        value = AsString('''
 -Xsection-split
'''))

Setting(name = 'AR', 
        replace = False,
        value = '$ROOT/ldcr_tools/diab/5.0a/win32/bin/dar.exe')

Setting(name = 'CPP', 
        replace = False,
        value = '$ROOT/ldcr_tools/diab/5.0a/win32/bin/dcc.exe')

Setting(name = 'CC', 
        replace = False,
        value = '$ROOT/ldcr_tools/diab/5.0a/win32/bin/dcc.exe')

Setting(name = 'CCCOM', 
        replace = False,
        value = '$CC $CCFLAGS 2>&1 | $TEE ${TARGET.base}.err')

Setting(name = 'LINK', 
        replace = False,
        value = '$ROOT/ldcr_tools/diab/5.0a/win32/bin/dld.exe')

Setting(name = 'LINKCOM', 
        replace = False,
        value = '$LINK $LINKFLAGS')

Setting(name = 'AS', 
        replace = False,
        value = '$ROOT/ldcr_tools/diab/5.0a/win32/bin/das.exe')

Setting(name = 'ASCOM', 
        replace = False,
        value = '$AS $ASFLAGS')

Setting(name = 'CPPDEFPREFIX', 
        replace = False,
        value = '-D')

Setting(name = 'CPPAUTOINCPREFIX',
        replace = False,
        value = '-i=')

Setting(name = 'CPPAUTOINCSUFFIX',
        replace = False,
        value = '')

Setting(name = 'INCPREFIX', 
        replace = False,
        value = "-I")

Setting(name = 'CPPFLAGS', 
        replace = False,
        value = AsString('''
 -E
 -D asm
 -WDDIABLIB=$ROOT/ldcr_tools/diab/5.0a
'''))

Setting(name = 'LIB_CCFLAGS',
        replace = False,
        value = AsString('''
 -Xsection-split
'''))

Setting(name = 'CCFLAGS', 
        replace = False,
        value = AsString('''
 $_CPPINCFLAGS
 $_CPPDEFFLAGS
 $_CPPAUTOINC
 $USER_CCFLAGS
 -XO
 -g3
 -o $TARGET
 -tPPC555EN:simple
 -Xlicense-wait
 -Xlint
 -Xno-recognize-lib
 -Xenum-is-unsigned
 -Ximport
 -Xnested-interrupts
 -Xsmall-data=20
 -Xsmall-const=999999
 -Xforce-declarations
 -Xforce-prototypes
 -Xno-common
 -Xfull-pathname
 -Xclib-optim-off
 -Xsize-opt
 -Xmember-max-align=2
 -WDDIABLIB=$ROOT/ldcr_tools/diab/5.0a
 -c
 ${TARGET.base}.c
'''))

Setting(name = 'LINKFLAGS', 
        replace = False,
        value = AsString('''
 -Xremove-unused-sections
 -L /ldcr_tools/diab/5.0a/win32/lib
 -m7
 -tPPC555EN:simple
 -lc $ROOT/blois_HWI_vob_TCL/Software/Hwi/hwi_micro/src/memory_map.dld
 -WDDIABLIB=$ROOT/ldcr_tools/diab/5.0a
 -o ${TARGET.base}.elf
 -@O=${TARGET.base}.map
 -@lnkobj.lis
'''))

Setting(name = 'LINK_DEPS',
        replace = False,
        value = '$ROOT/blois_HWI_vob_TCL/Software/Hwi/hwi_micro/src/memory_map.dld')

Setting(name = 'EXTROM', 
        replace = False,
        value = AsString('''
'''))

Setting(name = 'INTROM', 
        replace = False,
        value = AsString('''
'''))

Setting(name = 'EXTRAM', 
        replace = False,
        value = AsString('''
'''))

Setting(name = 'INTRAM', 
        replace = False,
        value = AsString('''
'''))

Setting(name = 'NVM', 
        replace = False,
        value = AsString('''
'''))

Setting(name = 'ASFLAGS', 
        replace = False,
        value = AsString('''
 -g
 -tPPC555EN:simple
 -o $TARGET
 -WDDIABLIB=$ROOT/ldcr_tools/diab/5.0a
 $SOURCE
'''))

def PreprocessFunction(target, source, env):
    """Preprocess Function for mpc555_diab target
    
    This builder runs a preprocess operation to generate a .c file in the out directory
    It handles a variable number of injectors and also processes calibration items
    
    """
    log_str = "Generating target (for a r72513_gcc compiler) " + str(target[0]) + " from source " + str(source[0])
    logging.info(log_str)    
    src = str(source[0])
    tgt = str(target[0])   
    srcfile = open(src,'rU')
    tgtfile = open(tgt,'w')
    contents = srcfile.read()
      
    # Deal with modifying constant arrays to MAX injectors
    contents = re.sub(r'(\[\s*)APP_NUMBER_OF_INJECTORS_CPV(\s*\])',r'\1APP_MAX_NUMBER_OF_INJECTORS_CPV\2',contents)
    contents = contents.splitlines()
    
    # Find all legal APV bar ESM_ names which are declarations or externs
    pat_apvs = re.compile(r'([A-Z_]{3}|IN)(_[A-Z0-9_]+_)(APV|APT|DAT|DAT_\d+|BPX|BPY)$')
    pat_esm = re.compile(r'(ESM)(_[A-Z0-9_]+_)(APV|APT|DAT|DAT_\d+|BPX|BPY)$')    
    p = Popen("ctags --language-force=c --sort=no -x --c-kinds=v " + src , stdout=PIPE)
    out_contents = []
    current_pos = 0
    
    for line in p.stdout:
        appdat_tag_found = False
        tags = line.split()
        # check for an Appdat tag
        if pat_esm.match(tags[0]):
            appdat_tag_found = True
            output_section = "#pragma use_section ESM_L2_APPDATA " + tags[0]
            output_header = "#pragma section ESM_L2_APPDATA \".esm_l2_appdata\" \".esm_l2_appdata\"" + "\n" + output_section
        elif pat_apvs.match(tags[0]):
            appdat_tag_found = True
            try:
                p = re.compile(r'(\\)')
                reformatted_src = p.sub('/', src)
                appdata = env['APPDATA']
                appdata_str = appdata[reformatted_src]
                output_header = appdata_str + " " + tags[0]
            except:
                output_section = "#pragma use_section APPDATA " + tags[0]
                output_header = "#pragma section APPDATA \".appdata\" \".appdata\"" + "\n" + output_section
        if appdat_tag_found == True:
            # write lines to output up to this appdat tag point    
            for x in range(current_pos,(int(tags[2]) - 1),1):
                out_contents.append(contents[x])
            current_pos = int(tags[2])
            out_contents.append(output_header)
            out_contents.append(contents[int(tags[2]) - 1])
    for x in range(current_pos,len(contents),1):
        out_contents.append(contents[x])
       
    tgtfile.write("\n".join(out_contents))
    # write blank line in case source does not have one, keeps GCC from issuing warning
    tgtfile.write("\n")
    srcfile.close
    tgtfile.close
    return None

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

