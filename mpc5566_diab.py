from subprocess import Popen, PIPE
from project import Setting, AsString
import logging
import re

logging.info("Setting target toolchain to " + __name__)

Setting(name = 'AR', 
        replace = False,
        value = '$ROOT/ldcr_tools/diab/5.6.1.0/win32/bin/dar.exe')

Setting(name = 'CPP', 
        replace = False,
        value = '$ROOT/ldcr_tools/gnu/GNUSH-ELF/v0603/sh-elf/bin/sh-elf-cpp.exe')

Setting(name = 'CC', 
        replace = False,
        value = '$ROOT/ldcr_tools/diab/5.6.1.0/win32/bin/dcc.exe')

Setting(name = 'CCCOM', 
        replace = False,
        value = '$CC $CCFLAGS')

Setting(name = 'LINK', 
        replace = False,
        value = '$ROOT/ldcr_tools/diab/5.6.1.0/win32/bin/dld.exe')

Setting(name = 'LINKCOM', 
        replace = False,
        value = '$LINK $LINKFLAGS')

Setting(name = 'AS', 
        replace = False,
        value = '$ROOT/ldcr_tools/diab/5.6.1.0/win32/bin/das.exe')

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
 -WDDIABLIB=$ROOT/ldcr_tools/diab/5.6.1.0
'''))

Setting(name = 'LIB_CCFLAGS',
        replace = False,
        value = AsString('''
 -Xsection-split
'''))

Setting(name = 'EXTROM', 
        replace = False,
        value = AsString('''
 -Xname-code=.ext_rom
 -Xname-const=.ext_far_const
 -Xname-sconst=.ext_rom
 -Xname-string=.ext_rom
 -Xname-uconst=.ext_far_const
 -Xname-usconst=.ext_rom
'''))

Setting(name = 'INTROM', 
        replace = False,
        value = AsString('''
'''))

Setting(name = 'ESML2ROM', 
        replace = False,
        value = AsString('''
 -Xname-const=.esm_l2_int_rom
 -Xname-code=.esm_l2_int_rom
 -Xname-sconst=.esm_l2_int_rom
 -Xname-string=.esm_l2_int_rom
 -Xname-uconst=.esm_l2_int_rom
 -Xname-usconst=.esm_l2_int_rom         
'''))

Setting(name = 'EXTRAM', 
        replace = False,
        value = AsString('''
 -Xname-data=.extram
 -Xname-sdata=.extram
 -Xname-udata=.extram 
 -Xname-usdata=.extram
'''))

Setting(name = 'INTRAM', 
        replace = False,
        value = AsString('''
'''))

Setting(name = 'ESML2RAM', 
        replace = False,
        value = AsString('''
 -Xname-data=.esm_l2_ram
 -Xname-sdata=.esm_l2_ram
 -Xname-udata=.esm_l2_ram 
 -Xname-usdata=.esm_l2_ram        
'''))

Setting(name = 'NVM', 
        replace = False,
        value = AsString('''
 -Xname-data=.nvmdata
 -Xname-sdata=.nvmdata
 -Xname-udata=.nvmdata 
 -Xname-usdata=.nvmdata
'''))

Setting(name = 'ASFLAGS', 
        replace = False,
        value = AsString('''
 -g
 -tPPC5566EN:simple
 -o $TARGET
 -WDDIABLIB=$ROOT/ldcr_tools/diab/5.6.1.0
 $SOURCE
'''))

Setting(name = 'TGT_5566', 
        replace = False,
        value = AsString('''
 -tPPC5566EN:simple
''')) 
Setting(name = 'TGT_5554', 
        replace = False,
        value = AsString('''
 -tPPC5554EN:simple
''')) 

Setting(name = 'CCFLAGS', 
        replace = False,
        value = AsString('''
 $_CPPINCFLAGS
 $_CPPDEFFLAGS
 $_CPPAUTOINC
 $USER_CCFLAGS
 -I $ROOT/ldcr_tools/diab/5.6.1.0/include
 -I src/lib
 -o $TARGET 
 -Xlicense-wait 
 -Xno-recognize-lib 
 -Xenum-is-unsigned
 -Ximport 
 -Xnested-interrupts 
 -Xlint 
 -Xforce-declarations 
 -Xforce-prototypes 
 -Xfull-pathname
 -Xdebug-dwarf1 
 -Xclib-optim-off 
 -Xsize-opt
 -Xsmall-const=9999999999
 -Xsmall-data=0
 -Xaddr-sconst=0x11
 -Xaddr-sdata=0x11
 -Xno-common 
 -i=mem_section_ram.h
 -i=mem_section_int_rom.h
 -i=mem_section_const.h
 -i=autosar_mem_sections.h
 -i=calib.h 
 -D _HWI_BASE_
 -WDDIABLIB=$ROOT/ldcr_tools/diab/5.6.1.0
 -c
 -g3
 -XO
 ${TARGET.base}.c
'''))

Setting(name = 'LINKFLAGS', 
        replace = False,
        value = AsString('''         
 -L $ROOT/ldcr_tools/diab/5.6.1.0/win32/lib
 -m7
 -tPPC5566EN:simple
 -lc src/hwi/src/hwi_memory_map.dld 
 -Xstop-on-warning
 -Xremove-unused-sections
 -WDDIABLIB=$ROOT/ldcr_tools/diab/5.6.1.0
 -o ${TARGET.base}.elf
 -@O=${TARGET.base}.map
 -@lnkobj.lis
'''))

Setting(name = 'LINK_DEPS',
        replace = False,
        value = 'src/hwi/src/hwi_memory_map.dld')
        
def PreprocessFunction(target, source, env):
    """Preprocess Function for mpc5554_diab target
    
    This builder runs a preprocess operation to generate a .c file in the out directory
    It handles a variable number of injectors and also processes calibration items
    
    """
    log_str = "Generating target (for a mpc5566_diab compiler) " + str(target[0]) + " from source " + str(source[0])
   
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
    pat_const_cpv = re.compile(r'(CONST)(_\w+_)(CPV)$')
    tagsfile = open(tgt + '.tags','rU')
    out_contents = []
    current_pos = 0
  
    try:
        # make sure any windows paths are turned into unix ones
        regex = re.compile(r'(\\)')
        reformatted_src = regex.sub('/', src)
        appdata = env['APPDATA_SECTION']
        appdata_str = appdata[reformatted_src]
    except:
    	try:
            appdata_str = env['APPDATA_DEFAULT']
    	except:
            appdata_str = '.appdata'

    appdata_default_section = '#pragma section APPDATA "' + appdata_str + '" "' + appdata_str + '"\n#pragma use_section APPDATA'
    log_str = log_str + " using APPDATA_SECTION as " + appdata_str
    logging.info(log_str)
           
    for line in tagsfile:
        appdat_tag_found = False
        tags = line.split()
        # check for an Appdat tag
        if pat_apvs.match(tags[0]):
            appdat_tag_found = True
            output_header = appdata_default_section + " " + tags[0]
        elif pat_const_cpv.match(tags[0]):
            appdat_tag_found = True
            output_header = appdata_default_section + " " + tags[0]

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
    tagsfile.close
    return None
        
def LinkFunction(target, source, env, for_signature):
    """Link Function for an mpc5554_diab target
        
    This builder runs a link operation
    
    """
    log_str = "Generating node target lnkobj_diab.lis" + " from " + str(env['LINKLIST'])   
    logging.info(log_str)
    src = str(env['LINKLIST'])
    tgt = "lnkobj_diab.lis"   
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
    
    

