#!/usr/bin/env python
"""Prints out memory usage information for DW10F in decimal bytes"""
import sys
import re
import os
import subprocess
import glob
import getopt
import fnmatch

verbose = False
debug = False
org = False
unit = False

def main():
    global verbose, debug, org, unit

    CLEARTOOL_CMD = 'cleartool'
    CLEARTOOL_SUB_CMD = 'ls'
    try:
        __version__ = subprocess.Popen([CLEARTOOL_CMD, CLEARTOOL_SUB_CMD, __file__],stdout=subprocess.PIPE).communicate()[0]
    except:
        __version__ = "unknown"
    print "Version", __version__

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hvdou", ["help", "verbose", "debug", "org", "unit"])
    except getopt.GetoptError, err:
        # print help information and exit:
        print str(err)
        help()
        exit(2)

    for o, a in opts:
        if o in ("-v", "--verbose"):
            verbose = True
        elif o in ("-d", "--debug"):
            debug = True
        elif o in ("-o", "--org"):
            org = True
        elif o in ("-u", "--unit"):
            unit = True
        elif o in ("-h", "--help"):
            help()
            exit(2)
        else:
            assert False, "unhandled option"
    
    if unit:
        analyse_units()
    else:
        analyse_map(args)

# Analyze the mapfile to extract memory usage (--verbose and --org options)
def analyse_map(args_par):    
    try:
        mapfile = args_par[0]                       # Use the mapfile specified
    except IndexError:
        try:
            mapfile = glob.glob('*.map')[0]         # Or try the 1st mapfile found
        except IndexError:
            print "Couldn't find a map file"
            exit(1)

    try:
        fdmap = open(mapfile, 'r')
    except IOError:
            print "Couldn't open map file", mapfile
            exit(1)
    print "Using mapfile", mapfile

    # Constants
    START_PFLASH            = int('0xa0000000', 16)         # uncached address range
    DCACHE_LDRAM_SIZE       = 2048                          # logical config
    ICACHE_SPRAM_SIZE       = 16384                         # logical config
    LDRAM_SIZE              = 131072                        # physical size
    OVRAM_SIZE              = 8192                          # physical size
    SPRAM_SIZE              = 40960                         # physical size
    PCP_SIZE                = 49152                         # physical size
    DEVRAM_SIZE             = 2097152                       # physical size
    DEVRAM_OVERFLOW_ATI     = 131072                        # logical config
    DEVRAM_OVERFLOW_APP     = 262144                        # logical config
    DEVRAM_CAL              = 1703936                       # logical config
    EDRAM                   = 524288                        # physical size
    EEPROM_SIZE             = 32768                         # physical size
    A7_RES_SIZE             = 4                             # logical config

    RAM_SYMBOLS = [
        "__SP_END",
        "__SP_INIT",
        "__CSA_BEGIN",
        "__CSA_END",
        "_lc_gb_initialized_spram_code_in_ram",
        "_lc_ge_initialized_spram_code_in_ram",
        "OVRAM_START",
        "OVRAM_END_PLUS_1",
        "RAM_START_NO_CACHE_ADDRESS_PTR",
        "RAM_END_NO_CACHE_ADDRESS_PTR",
        "__RAM_BYP_FREE_START",
        "START_APP_LDRAM_A",
        "END_APP_LDRAM_A",
        "START_APP_LDRAM_B",
        "END_APP_LDRAM_B",
        "START_APP_SPRAM_A",
        "END_APP_SPRAM_A",
        "START_APP_SPRAM_B",
        "END_APP_SPRAM_B",
        "DEV_OVERFLOW_RAM_START_ADDRESS_PTR",
        "DEV_OVERFLOW_RAM_END_ADDRESS_PTR",
        "__DEVRAM_OVERFLOW_START",
        "_DEVRAM_OVERFLOW_SIZE",
        "START_DELPHI_RAM_B",
        "START_DELPHI_RAM_C1",
        "START_DELPHI_RAM_C2",
        "START_DELPHI_RAM_D",
        "START_DELPHI_RAM_E",
        "START_DELPHI_RAM_F",
        "START_DELPHI_RAM_G",
        "START_DELPHI_RAM_H",
        "START_DELPHI_RAM_I",
        "START_DELPHI_RAM_J",
        "START_DELPHI_RAM_K",
        "START_DELPHI_RAM_L",
        "START_DELPHI_RAM_M",
        "START_DELPHI_RAM_N",
        "END_DELPHI_RAM_B",
        "END_DELPHI_RAM_C1",
        "END_DELPHI_RAM_C2",
        "END_DELPHI_RAM_D",
        "END_DELPHI_RAM_E",
        "END_DELPHI_RAM_F",
        "END_DELPHI_RAM_G",
        "END_DELPHI_RAM_H",
        "END_DELPHI_RAM_I",
        "END_DELPHI_RAM_J",
        "END_DELPHI_RAM_K",
        "END_DELPHI_RAM_L",
        "END_DELPHI_RAM_M",
        "END_DELPHI_RAM_N",
        "START_RB_RAM_A",
        "START_RB_RAM_B",
        "START_RB_RAM_C1",
        "START_RB_RAM_C2",
        "START_RB_RAM_C3",
        "START_RB_RAM_C4",
        "START_RB_RAM_D",
        "START_RB_RAM_E",
        "START_RB_RAM_F",
        "START_RB_RAM_G",
        "START_RB_RAM_H",
        "START_RB_RAM_I",
        "START_RB_RAM_J",
        "END_RB_RAM_A",
        "END_RB_RAM_B",
        "END_RB_RAM_C1",
        "END_RB_RAM_C2",
        "END_RB_RAM_C3",
        "END_RB_RAM_C4",
        "END_RB_RAM_D",
        "END_RB_RAM_E",
        "END_RB_RAM_F",
        "END_RB_RAM_G",
        "END_RB_RAM_H",
        "END_RB_RAM_I",
        "END_RB_RAM_J",
        "START_FORD_RAM_A",
        "START_FORD_RAM_B",
        "START_FORD_RAM_C1",
        "START_FORD_RAM_C2",
        "START_FORD_RAM_C3",
        "START_FORD_RAM_D",
        "START_FORD_RAM_E",
        "START_FORD_RAM_F1",
        "START_FORD_RAM_F2",
        "START_FORD_RAM_G",
        "START_FORD_RAM_H",
        "END_FORD_RAM_A",
        "END_FORD_RAM_B",
        "END_FORD_RAM_C1",
        "END_FORD_RAM_C2",
        "END_FORD_RAM_C3",
        "END_FORD_RAM_D",
        "END_FORD_RAM_E",
        "END_FORD_RAM_F1",
        "END_FORD_RAM_F2",
        "END_FORD_RAM_G",
        "END_FORD_RAM_H",
        "START_UNACCOUNTED_RAM_A",
        "START_UNACCOUNTED_RAM_B",
        "START_UNACCOUNTED_RAM_C",
        "END_UNACCOUNTED_RAM_A",
        "END_UNACCOUNTED_RAM_B",
        "END_UNACCOUNTED_RAM_C",
        "URAM1_START_ADDRESS_PTR",
        "URAM1_END_ADDRESS_PTR"
    ]

    ROM_SYMBOLS = [
            "_sta_app_code_block_desc",
            "_end_code_rom",
            "_lc_ge_initialized_extram_data_in_rom",
            "_lc_ge_pcp_data_rom",
            "_lc_gb_pcp_data_rom",
            "_lc_gb_pcp_code_rom",
            "_sta_app_data_ident_desc",
            "__DS0_FREE_START",
            "__DS0_FREE_END",
            "__DS0_DATA_START",
            "__ENVRAM_CHECKSUM_END",
            "__ASW0_FREE_START",
            "__DS0_FREE_START",
            "_end_app_vectors_table",
            "_end_app_code_cks_esm_ram_desc",
            "START_DELPHI_CODE_A",
            "START_DELPHI_CODE_B",
            "START_DELPHI_CODE_C",
            "START_DELPHI_CODE_D",
            "START_DELPHI_CODE_E",
            "START_DELPHI_CODE_F",
            "START_DELPHI_CODE_G",
            "END_DELPHI_CODE_A",
            "END_DELPHI_CODE_B",
            "END_DELPHI_CODE_C",
            "END_DELPHI_CODE_D",
            "END_DELPHI_CODE_E",
            "END_DELPHI_CODE_F",
            "END_DELPHI_CODE_G",
            "START_RB_CODE_A",
            "START_RB_CODE_B",
            "START_RB_CODE_D",
            "END_RB_CODE_A",
            "END_RB_CODE_B",
            "END_RB_CODE_D",
            "START_FORD_CODE_A",
            "START_FORD_CODE_B",
            "END_FORD_CODE_A",
            "END_FORD_CODE_B",
            "START_DELPHI_CAL_A",
            "START_RB_CAL_A",
            "START_RB_CAL_B",
            "START_FORD_CAL_A",
            "END_DELPHI_CAL_A",
            "END_RB_CAL_A",
            "END_RB_CAL_B",
            "END_FORD_CAL_A",
            ]


    all_symbols = RAM_SYMBOLS + ROM_SYMBOLS

    # Extract symbols and their addresses from the mapfile
    for aline in fdmap:                         # for every line in the map file
        for label in all_symbols:               # for every label
            if ( (aline.startswith(label)) and (aline.split()[0] == label) ):     # if label found at start of line
                try:
                    addr = int(aline.split()[2],16)                 # get column 3 and convert to decimal
                    if ((addr >= int("0x80000000",16)) and (addr < int("0x90000000",16))):
                        addr += int("0x20000000",16)                # make cached addresses appear non-cached by offset
                    exec("%s = %s" % (label, addr))                 # assign the label value to the symbol
                    if debug:
                        print("%s = %s" % (label, hex(addr)))
                except IndexError:
                    pass

    # Calculate statistics
    ldram_used = (
            (END_APP_LDRAM_A - START_APP_LDRAM_A) +
            (END_APP_LDRAM_B - START_APP_LDRAM_B) +
            (RAM_END_NO_CACHE_ADDRESS_PTR - RAM_START_NO_CACHE_ADDRESS_PTR)
            )

    devram_overflow_used = DEV_OVERFLOW_RAM_END_ADDRESS_PTR - __DEVRAM_OVERFLOW_START
    devram_overflow_free = _DEVRAM_OVERFLOW_SIZE - devram_overflow_used
    # The stack pointer is initialised to a  high address and points to low addresses as the stack grows. 
    stack_size = __SP_INIT - __SP_END    
    csa_size = __CSA_END - __CSA_BEGIN  
    spram_used = (
            (END_APP_SPRAM_A - START_APP_SPRAM_A) +
            (END_APP_SPRAM_B - START_APP_SPRAM_B)
            )
    spram_code_used = _lc_ge_initialized_spram_code_in_ram - _lc_gb_initialized_spram_code_in_ram
    spram_free = SPRAM_SIZE - spram_used - spram_code_used - ICACHE_SPRAM_SIZE
    ovram_used = OVRAM_END_PLUS_1 - OVRAM_START
    ovram_free = OVRAM_SIZE - ovram_used
    pflash_reserved = _sta_app_code_block_desc - START_PFLASH
    pflash_code_used = _end_code_rom - _sta_app_code_block_desc
    pflash_initdata_used = _lc_ge_initialized_extram_data_in_rom - _lc_ge_pcp_data_rom
    pflash_pcp_used = _lc_ge_pcp_data_rom - _lc_gb_pcp_code_rom 
    pflash_total_code_used = pflash_code_used + pflash_pcp_used + pflash_initdata_used
    pflash_code_free = _sta_app_data_ident_desc - _lc_ge_initialized_extram_data_in_rom
    pflash_cal_used = __DS0_FREE_START - _sta_app_data_ident_desc
    pflash_cal_free = __DS0_FREE_END - __DS0_FREE_START
    ldram_total_used = stack_size + csa_size + DCACHE_LDRAM_SIZE + ldram_used
    appram_total_used = ldram_used + ovram_used + spram_used + devram_overflow_used
    ldram_free = LDRAM_SIZE - ldram_total_used
    total_ram_free = ldram_free + spram_free + ovram_free + devram_overflow_free
    onchip_ram_free = ldram_free + spram_free + ovram_free
    delphi_code_rom = (
                    (END_DELPHI_CODE_A - START_DELPHI_CODE_A) +
                    (END_DELPHI_CODE_B - START_DELPHI_CODE_B) +
                    (END_DELPHI_CODE_C - START_DELPHI_CODE_C) +
                    (END_DELPHI_CODE_D - START_DELPHI_CODE_D) +
                    (END_DELPHI_CODE_E - START_DELPHI_CODE_E) +
                    (END_DELPHI_CODE_F - START_DELPHI_CODE_F) +
                    (END_DELPHI_CODE_G - START_DELPHI_CODE_G)
                )

    rb_code_rom = (
                (END_RB_CODE_A - START_RB_CODE_A) +
                (END_RB_CODE_B - START_RB_CODE_B) +
                (END_RB_CODE_D - START_RB_CODE_D)
            )

    ford_code_rom = (
                (END_FORD_CODE_A - START_FORD_CODE_A) +
                (END_FORD_CODE_B - START_FORD_CODE_B)
                )

    delphi_ram = (
            (END_DELPHI_RAM_B - START_DELPHI_RAM_B) +
            (END_DELPHI_RAM_C1 - START_DELPHI_RAM_C1) +
            (END_DELPHI_RAM_C2 - START_DELPHI_RAM_C2) +
            (END_DELPHI_RAM_D - START_DELPHI_RAM_D) +
            (END_DELPHI_RAM_E - START_DELPHI_RAM_E) +
            (END_DELPHI_RAM_F - START_DELPHI_RAM_F) +
            (END_DELPHI_RAM_G - START_DELPHI_RAM_G) +
            (END_DELPHI_RAM_H - START_DELPHI_RAM_H) +
            (END_DELPHI_RAM_I - START_DELPHI_RAM_I) +
            (END_DELPHI_RAM_J - START_DELPHI_RAM_J) +
            (END_DELPHI_RAM_K - START_DELPHI_RAM_K) +
            (END_DELPHI_RAM_L - START_DELPHI_RAM_L) +
            (END_DELPHI_RAM_M - START_DELPHI_RAM_M) +
            (END_DELPHI_RAM_N - START_DELPHI_RAM_N)
            )

    rb_ram = (
            (END_RB_RAM_A - START_RB_RAM_A) +
            (END_RB_RAM_B - START_RB_RAM_B) +
            (END_RB_RAM_C1 - START_RB_RAM_C1) +
            (END_RB_RAM_C2 - START_RB_RAM_C2) +
            (END_RB_RAM_C3 - START_RB_RAM_C3) +
            (END_RB_RAM_C4 - START_RB_RAM_C4) +
            (END_RB_RAM_D - START_RB_RAM_D) +
            (END_RB_RAM_E - START_RB_RAM_E) +
            (END_RB_RAM_F - START_RB_RAM_F) +
            (END_RB_RAM_G - START_RB_RAM_G) +
            (END_RB_RAM_H - START_RB_RAM_H) +
            (END_RB_RAM_I - START_RB_RAM_I) +
            (END_RB_RAM_J - START_RB_RAM_J)
            )

    ford_ram = (
            (END_FORD_RAM_A - START_FORD_RAM_A) +
            (END_FORD_RAM_B - START_FORD_RAM_B) +
            (END_FORD_RAM_C1 - START_FORD_RAM_C1) +
            (END_FORD_RAM_C2 - START_FORD_RAM_C2) +
            (END_FORD_RAM_C3 - START_FORD_RAM_C3) +
            (END_FORD_RAM_D - START_FORD_RAM_D) +
            (END_FORD_RAM_E - START_FORD_RAM_E) +
            (END_FORD_RAM_F1 - START_FORD_RAM_F1) +
            (END_FORD_RAM_F2 - START_FORD_RAM_F2) +
            (END_FORD_RAM_G - START_FORD_RAM_G) +
            (END_FORD_RAM_H - START_FORD_RAM_H)
            )

    unaccounted_ram = (
            (END_UNACCOUNTED_RAM_A - START_UNACCOUNTED_RAM_A) +
            (END_UNACCOUNTED_RAM_B - START_UNACCOUNTED_RAM_B) +
            (END_UNACCOUNTED_RAM_C - START_UNACCOUNTED_RAM_C) 
            )
    delphi_cal_rom = (END_DELPHI_CAL_A - START_DELPHI_CAL_A)
    rb_cal_rom = (END_RB_CAL_A - START_RB_CAL_A) + (END_RB_CAL_B - START_RB_CAL_B)
    ford_cal_rom = (END_FORD_CAL_A - START_FORD_CAL_A)
    total_delphi_rom = delphi_code_rom + delphi_cal_rom
    total_rb_rom = rb_code_rom + rb_cal_rom
    total_ford_rom = ford_code_rom + ford_cal_rom
    
    total_physical_ram              = LDRAM_SIZE + OVRAM_SIZE + SPRAM_SIZE + PCP_SIZE + DEVRAM_SIZE
    total_onchip_physical_ram       = LDRAM_SIZE + OVRAM_SIZE + SPRAM_SIZE + PCP_SIZE
    total_onchip_physical_app_ram   = LDRAM_SIZE + OVRAM_SIZE + SPRAM_SIZE 
    total_onchip_available_app_ram = (
            (LDRAM_SIZE + OVRAM_SIZE + SPRAM_SIZE) - 
            (DCACHE_LDRAM_SIZE + ICACHE_SPRAM_SIZE + A7_RES_SIZE + stack_size + csa_size + spram_code_used)
            )

    # Display detailed info
    if verbose:
        print
        print "[01]     Instruction cache size (SPRAM)           =", ICACHE_SPRAM_SIZE
        print "[02]     SPRAM code used (SPRAM)                  =", spram_code_used
        print "[03]     Stack size (LDRAM)                       =", stack_size
        print "[04]     CSA size (LDRAM)                         =", csa_size
        print "[05]     Data cache size (LDRAM)                  =", DCACHE_LDRAM_SIZE
        print "[06]     Application RAM used (LDRAM)             =", ldram_used
        print "[07]     Application RAM used (SPRAM)             =", spram_used
        print "[08]     Application RAM used (OVRAM)             =", ovram_used
        print "[09]     Application RAM used (DEVRAM)            =", devram_overflow_used
        print "[10]     Total LDRAM used                         = %i  (STACK = %i, CSA = %i, DCACHE = %i, APP = %i)" % (ldram_total_used, stack_size, csa_size, DCACHE_LDRAM_SIZE, ldram_used) 
        print "[11]     Total application RAM used               = %i  (LDRAM = %i, SPRAM = %i, OVRAM = %i, DEVRAM = %i)" %( appram_total_used, ldram_used, spram_used, ovram_used, devram_overflow_used)
        print "[12]     ROM reserved [BM/FL/EOL] (PFLASH)        =", pflash_reserved
        print "[13]     ROM code used (PFLASH)                   = %i (CODE/CONST = %i, PCP = %i, INITDATA = %i)" % (pflash_total_code_used, pflash_code_used, pflash_pcp_used, pflash_initdata_used)
        print "[14]     ROM cal used (PFLASH)                    =", pflash_cal_used
        print "-----------------------------------------------------------------------------------------------------------"
    # Display simple summary
    print
    print "[15]     RAM free (on-chip)                       = %i    (LDRAM = %i, SPRAM = %i, OVRAM = %i)" % (onchip_ram_free, ldram_free, spram_free, ovram_free)
    print "[16]     RAM free                                 = %i  (LDRAM = %i, SPRAM = %i, OVRAM = %i, DEVRAM = %i)" % (total_ram_free, ldram_free, spram_free, ovram_free, devram_overflow_free)
    print "[17]     ROM code free                            =", pflash_code_free 
    print "[18]     ROM cal free                             =", pflash_cal_free
    print
    print "[19]     ATI NoHooks RAM start addr               =", hex(__RAM_BYP_FREE_START)
    print "[20]     ATI NoHooks ROM code start addr          =", hex(__ASW0_FREE_START)
    print "[21]     ATI NoHooks ROM cal start addr           =", hex(__DS0_FREE_START)
    # Display ROM usage by organization
    if org:
        print "-----------------------------------------------------------------------------------------------------------"
        print
        print "[22]     Delphi code ROM                          = ", delphi_code_rom
        print "[23]     Bosch code ROM                           = ", rb_code_rom
        print "[24]     Ford code ROM                            = ", ford_code_rom
        print "[25]     Delphi cal ROM                           = ", delphi_cal_rom
        print "[26]     Bosch cal ROM                            = ", rb_cal_rom
        print "[27]     Ford cal ROM                             = ", ford_cal_rom
        print "-----------------------------------------------------------------------------------------------------------"
        print
        print "[28]     Total Delphi ROM                         = ", total_delphi_rom
        print "[29]     Total Bosch ROM                          = ", total_rb_rom
        print "[30]     Total Ford ROM                           = ", total_ford_rom
        print "[31]     Delphi RAM                               = ", delphi_ram
        print "[32]     Bosch RAM                                = ", rb_ram
        print "[33]     Ford RAM                                 = ", ford_ram
        print "[34]     Unaccounted RAM                          = ", unaccounted_ram

    # Display physical info
    if verbose:
        print "-----------------------------------------------------------------------------------------------------------"
        print
        print "[35]     Total physical RAM                       = %i (LDRAM = %i, SPRAM = %i, OVRAM = %i, PCPRAM = %i, DEVRAM = %i)" % (total_physical_ram, LDRAM_SIZE, SPRAM_SIZE, OVRAM_SIZE, PCP_SIZE, DEVRAM_SIZE)
        print "[36]     Total on-chip physical RAM               = %i (LDRAM = %i, SPRAM = %i, OVRAM = %i, PCPRAM = %i)" % (total_onchip_physical_ram, LDRAM_SIZE, SPRAM_SIZE, OVRAM_SIZE, PCP_SIZE)
        print "[37]     Total on-chip physical application RAM   = %i (LDRAM = %i, SPRAM = %i, OVRAM = %i)" % (total_onchip_physical_app_ram, LDRAM_SIZE, SPRAM_SIZE, OVRAM_SIZE)
        print "[38]     Total on-chip available application RAM  = %i ( [37] - ( [01] + [02] + [03] + [04] + [05] ) )" % (total_onchip_available_app_ram)

    # Display detailed info
        print
        print
        print "NOTES\n"
        print "Application variables are stored in LDRAM, SPRAM, OVRAM and external DEVRAM"
        print "Some LDRAM is set aside for data cache, stack, and CSA.  The space used to store app vars is not contiguous"
        print
        print "[01]     SPRAM configured for instruction cache (fixed size)"
        print "[02]     SPRAM used for code"
        print "[03]     LDRAM configured for stack (fixed size)"
        print "[04]     LDRAM configured for context save area (fixed size)"
        print "[05]     LDRAM configured for data cache (fixed size)"
        print "[06]     LDRAM used for application variables (including DMA buffers)"
        print "[07]     SPRAM used for application variables"
        print "[08]     OVRAM used for application variables"
        print "[09]     External DEVRAM used for application variables"
        print "[10]     Total LDRAM used including system data (stack, CSA, DCACHE, application variables, DMA)"
        print "[11]     Total RAM used for application variables (LDRAM, SPRAM, OVRAM, External DEVRAM)"
        print "[12]     PFLASH used for boot, flash loader, end-of-line data"
        print "[13]     PFLASH used for code, constants, PCP code, ROM copies of intialized data"
        print "[14]     PFLASH used for calibration. Temporarily contains some non-cal consts due to insufficient code ROM"
        print "[22-30]  ROM usage by organization.  Doesn't include PCP, INITDATA.  May not include alignment, padding bytes"
        print "[31-33]  RAM usage by organization.  May not include alignment, padding bytes"
        print "         NOTE: RTOS and Vector is assigned to Delphi and doesn't include CSA or stack"
        print "[34]     RAM usage that needs to be assigned to a user for accounting"

    # Display warning when URAM goes above 0xD00096FF
    if URAM1_END_ADDRESS_PTR > 0xD00096FF:
        print
        print
        print "-----------------------------------------------------------------------------------------------------------"
        print "-----------------------------------------------------------------------------------------------------------"
        print "\t\t\t\t\tURAM STATUS WARNING!!!"
        print "URAM above the accepted limit of 0xD00096FF, will be corrupted by boot after reset. "
        print "-----------------------------------------------------------------------------------------------------------"
        print "-----------------------------------------------------------------------------------------------------------"

    fdmap.close()

# Analyze the object files using the tricore-size utility (---units option)
def analyse_units():
    global mem_sizes, wilds, ALL_SECTIONS, CODE_SECTIONS, CAL_SECTIONS, RAM_SECTIONS, CONST_SECTIONS, IGNORE_SECTIONS, pname, oname, dname, fname, secname_not_found_list
    print "Analysing compilation units..."
    # Get a list of object files to analyze from config.py
    filelist_source = list()
    regex = re.compile(r"'(.*?)'")
    fdconfig = open('config.py','r')
    for aline in fdconfig.readlines():
        found_line = re.search('SourceFile|ObjectFile', aline)
        if found_line:
            commented_out = re.match(r' *#.*', aline)
            if commented_out:
                pass
            else:
                aline = re.search(regex,aline).group()
                filelist_source.append(re.sub(regex, r'\1', aline))
    fdconfig.close()
    filelist = filelist_source
    total = len(filelist)
    numfiles = 0

    TRICORE_SIZE_CMD = '../../tcg_cots_tool_vob/HighTec/3.4.5.9/TriCore/bin/tricore-size.exe'
    TRICORE_SIZE_OPT = '-A'

    # NOTE: CAREFUL WITH WILDCARDS - OTHERWISE SECTIONS MAY BE ADDED MULTIPLE TIMES!!
    CODE_SECTIONS = [
            ".app_code_block_desc1",
            ".app_code_block_desc2",
            ".app_code_cks_esm_ram_desc",
            ".trap_vector_table",
            ".text.s_s_bkg_code",
            ".os_text",
            ".text.app_code_rom",
            ".os_intvect",
            ".text.app_code",
            ".text",
            ".text.M*",
            ".startup_code.a0",
            ".startup_code.a1",
            ".inttab",
            ".text.esm_code",
            ".code.rb.mon",
            ".text.esm_mic_code",
            ".code.rb.normal",
            ".code.fo.cvc",
            ".code.fo.stopstart",
            ".code.fo.dat",
            ".code.fo.scr",
            ".code.fo.dap",
            ".code.fo.cpf",
            ".code.rb.fast",
            ".text.c_i_code",
            ".pcode",
            ".text.FSIN",
            ]

    CONST_SECTIONS = [
            ".app_data_block_desc1",
            ".rodata.app_const",
            ".rodata.p_l_com_const",
            ".rodata.nvm_const",
            ".rodata",
            ".rodata.a4",
            ".rodata.a4.os_pid2",
            ".rodata.a2",
            ".rodata.a2.os_pid2",
            ".rodata.a1",
            ".rodata.a1.os_pid2",
            ".rodata.os.pid2",
            ".rodata.os_pid",
            ".rodata.os_pird",
            ".rodata.os_pnird",
            ".rodata.esm_const",
            ".rodata.p_l_esm_const",
            ".rodata.esm_mic_const",
            ".rodata.fo.cvc",
            ".rodata.fo.stopstart",
            ".rodata.fo.cpf",
            ".rodata.fo.dat",
            ".rodata.fo.scr",
            ".rodata.fo.dap",
            ".rodata.c_i_const",
            ".sdata.rodata.f_m_const",
            ".sdata.rodata.dti_const",
            ".sdata.rodata.rb",
            ".sdata.rb.ptavect",
            ".sdata.rodata.i_c_const",
            ".sdata.rodata.rpc_const",
            ".sdata.rodata.hwi_const",
            ".sdata.rodata.p_l_aps_const",
            ".sdata.rodata.p_l_inj_const",
            ".sdata.rodata.p_l_wrf_const",
            ".sdata.rodata.p_l_fie_const",
            ".sdata.rodata.p_l_lib_const",
            ".sdata.rodata.icv_const",
            ".sdata.rodata.rpd_const",
            ".sdata.rodata.smc_const",
            ".sdata.rodata.ste_const",
            ".sdata.rodata.t_d_const",
            ".sdata.rodata.s_s_const",
            ".sdata.rodata.s_s_lib_const",
            ".sdata.rodata.app_stub_const",
            ".app_data_ident_desc1",
            ".app_data_cks_desc",
            ".app_data_cks_esm",
            ".rodata.rb"
    ]

    CAL_SECTIONS = [
            ".rodata.appdata",
            ".rodata.p_l_lib_appdata",
            ".rodata.p_l_com_appdata",
            ".rodata.hwi_appdata",
            ".rodata.p_l_aps_appdata",
            ".rodata.p_l_inj_appdata",
            ".rodata.p_l_wrf_appdata",
            ".rodata.p_l_fie_appdata",
            ".rodata.i_c_appdata",
            ".rodata.rpc_appdata",
            ".rodata.f_m_appdata",
            ".rodata.dti_appdata",
            ".rodata.icv_appdata",
            ".rodata.rpd_appdata",
            ".rodata.smc_appdata",
            ".rodata.ste_appdata",
            ".rodata.t_d_appdata",
            ".rodata.s_s_appdata",
            ".rodata.s_s_lib_appdata",
            ".rodata.app_stub_appdata",
            ".sdata.rodata.nvm_appdata",
            ".rodata.esm_appdata",
            ".rodata.p_l_esm_appdata",
            ".rodata.esm_mic_appdata",
            ".rodata.c_i_appdata_1ms",
            ".rodata.c_i_appdata_2ms",
            ".rodata.c_i_appdata_5ms",
            ".rodata.c_i_appdata_10ms",
            ".rodata.c_i_appdata_20ms",
            ".rodata.c_i_appdata_30ms",
            ".rodata.c_i_appdata_40ms",
            ".rodata.c_i_appdata_50ms",
            ".rodata.c_i_appdata_100ms",
            ".rodata.c_i_appdata_200ms",
            ".rodata.c_i_appdata_250ms",
            ".rodata.c_i_appdata_1000ms",
            ".rodata.c_i_appdata_other",
            ".rodata.c_i_appdata",
            ".caldata.rb",
            ".caldata.fo.cvc",
            ".caldata.fo.cvc.7",
            ".caldata.fo.stopstart",
            ".caldata.fo.dat",
            ".caldata.fo.dat.8",
            ".caldata.fo.dap",
            ".caldata.fo.scr",
            ".caldata.fo.cpf",
            ".caldata.fo.cpf.9",
            ".rodata.rb.ptadata"
    ]

    RAM_SECTIONS = [
            ".pcpdata",
            ".section_pram_region",
            ".section_pcp_register",
            ".bdata.rb",
            ".zdata.rb",
            ".zbss.rb",
            ".bbss.rb",
            ".bss.esm_uram",
            ".bss.fo.dap",
            ".bss.fo.stopstart",
            ".bss.fo.dat",
            ".bss.fo.spram",
            ".bss.p_l_daq_ram",
            ".bss.rb.cycliccheck",
            ".bss.rb.nocycliccheck",
            ".bss.rb.usermon",
            ".bss.rb.slow",
            ".bss.rb.slow1",
            ".bss.rb.slow2",
            ".bss.rb.slow3",
            ".bss.rb.slow4",
            ".bss.rb.slow5",
            ".bss.rb.slow6",
            ".bss.rb.slow7",
            ".bss.rb.slow8",
            ".bss.rb.slow9",
            ".bss.rb.slow10",
            ".sdata.fo.dat",
            ".sdata.fo.dap",
            ".zbss",
            ".zdata",
            ".bbss.rb.protram",
            ".bss.rb.protram",
            ".bss.fo.protram",
            ".bss.eep_ram",
            ".bss.earlycleared",
            ".bss.srv_ram",
            ".bss.rb.nvmy",
            ".bss.fo.envram",
            ".data.rb.nvmy",
            ".data.fo.envram",
            ".sdata.rb",
            ".sdata.fo.cvc",
            ".sdata.fo.cpf",
            ".sdata.fo.scr",
            ".sdata.fo.stopstart",
            ".sdata.c_i_ram",
            ".sdata.os_pnid",
            ".sdata.a4",
            ".sdata.a2",
            ".sdata.a1",
            ".sdata.os_pnir",
            ".sdata.os_pnir2",
            ".sbss.eep_uram",
            ".sbss.rb",
            ".sbss.rb.ReIni",
            ".sbss",
            ".sbss.a4",
            ".sbss.a2",
            ".sbss.a1",
            ".sbss.os_cntr",
            ".sbss.os_pnur",
            ".sbss.cpf",
            ".sbss.fo.cvc",
            ".sbss.fo.stopstart",
            ".sbss.fo.dat",
            ".sbss.fo.dap",
            ".sbss.fo.scr",
            ".sbss.fo.cpf",
            ".sbss.app_stub_ram",
            ".sbss.c_i_ram",
            ".sbss.dds_ram",
            ".sbss.hwi_ram",
            ".sbss.i_c_ram",
            ".sbss.p_l_inj_ram",
            ".sbss.p_l_aps_ram",
            ".sbss.rpc_ram",
            ".sbss.p_l_wrf_ram",
            ".sbss.p_l_fie_ram",
            ".sbss.p_l_lib_ram",
            ".sbss.f_m_ram",
            ".sbss.dti_ram",
            ".sbss.icv_ram",
            ".sbss.rpd_ram",
            ".sbss.smc_ram",
            ".sbss.ste_ram",
            ".sbss.t_d_ram",
            ".sbss.s_s_ram",
            ".sbss.s_s_lib_ram",
            ".sbss.nvm_ram",
            ".sbss.esm_ram",
            ".bss.esm_ram",
            ".sbss.p_l_esm_ram",
            ".sbss.esm_mic_ram",
            ".bss.esm_mic_ram",
            ".bss.rb.usermon",
            ".data.rb",
            ".data.rb.initpwl",
            ".data",
            ".data.a4",
            ".data.a2",
            ".data.a1",
            ".data.os_pir",
            ".data.os_trace_ram",
            ".data.fo.dat",
            ".data.fo.stopstart",
            ".data.fo.cpf",
            ".data.fo.cvc",
            ".data.fo.dap",
            ".data.fo.scr",
            ".bss.rb.fast",
            ".bss.rb.restricted",
            ".bss.fo.restricted",
            ".bss.p_l_com_ram",
            ".bss.rb.mon",
            ".MoF_Ram",
            ".MoF_CplRam",
            ".MoF_DiaBitRam",
            ".bss.fo.cvc",
            ".bss.fo.cpf",
            ".bss.fo.scr",
            ".bss",
            ".bss.a4",
            ".bss.a2",
            ".bss.a1",
            ".bss.m*",
            ".bss.os_pur",
            ".bss.os_pur2",
            ".bss.os_trace_ram",
            ".bss.a4.os_pur2",
            ".bss.a2.os_pur2",
            ".stack",
            ".bss.nvm_copy_ram",
            ".bss.rb.medium",
            ".devram_section",
            ".sbss.c_i_100ms",
            ".sbss.p_l_wrf_100ms",
]

    # Lines that aren't section names
    IGNORE_SECTIONS = [
            "section",
            "Total",
            ".version_info",
            ".debug_abbrev",
            ".debug_info",
            ".debug_line",
            ".debug_frame",
            ".debug_pubnames",
            ".debug_aranges",
            ".debug_str",
            ".debug_ranges",
            ".boffs",
            ".unspecified_sections",
            ".VarEd_Info",
            ]

    ALL_SECTIONS = CODE_SECTIONS + CAL_SECTIONS + CONST_SECTIONS + RAM_SECTIONS

    code_size_cum = 0
    cal_size_cum = 0
    const_size_cum = 0
    ram_size_cum = 0
    secname_not_found_list = list()
    final = list()

    # Get a list of wildcard section names
    wilds = list()
    for secname in ALL_SECTIONS:
        if re.search('\*', secname):
            secname = fnmatch.translate(secname)
            wilds.append(secname)

    # For each object file, go through each line of output from the tricore-size command and check whether it
    # belongs to the code, const, cal or ram section.  If there are any new sections not categorized, then add
    # to a list of unhandled sections and print a warning so that the script may be corrected.
    for fname in filelist:
        exten = os.path.splitext(fname)[1]
        if exten == ".c" or exten == ".C":
            oname = os.path.splitext(os.path.split(fname)[1])[0]+'.o'
            dname = re.sub('src$','out',os.path.split(fname)[0])
            pname = os.path.join(dname, oname)
        else:
            oname = fname
            pname = fname

        mem_sizes = subprocess.Popen([TRICORE_SIZE_CMD, TRICORE_SIZE_OPT, pname],stdout=subprocess.PIPE).communicate()[0]
        code_size = 0
        cal_size = 0
        const_size = 0
        ram_size = 0
        here = 0

        code_size = search_sections(CODE_SECTIONS)
        cal_size = search_sections(CAL_SECTIONS)
        const_size = search_sections(CONST_SECTIONS)
        ram_size = search_sections(RAM_SECTIONS)
    
        code_size_cum += code_size
        cal_size_cum += cal_size
        const_size_cum += const_size
        ram_size_cum += ram_size
        numfiles += 1
        print >>sys.stderr, "%d/%-10d %s" % (numfiles, total, pname)

        if debug:
            print "Code size =", code_size
            print "Cal size =", cal_size
            print "Const size =", const_size
            print "RAM size =", ram_size

        final.append([oname, code_size, cal_size, const_size, ram_size])

    # Print sorted output 
    for col in range(5):
        print_sorted(col, final)

    if secname_not_found_list:
        print "************************************* WARNING ***************************************"
        print "The following sections need to be added to one of: CODE_SECTIONS, CONST_SECTIONS,"
        print "CAL_SECTIONS or RAM_SECTIONS.  The printed results are NOT correct."
        print "Please update this script and re-run"
        print secname_not_found_list
        print "************************************* WARNING ***************************************"

    print
    print "*****************************************************************************************************************" 
    print "NOTE: Depending on the linker options, the objects may be optimized to exclude unreferenced data in the final elf"
    print "*****************************************************************************************************************" 

    if debug:
        # Note: These numbers will be different from mapfile analysis due to different accounting methods...
        print "Total code size =", code_size_cum
        print "Total cal size =", cal_size_cum
        print "Total const size =", const_size_cum
        print "Total RAM size =", ram_size_cum

def search_sections(section_type):
    global secname_not_found_list
    cum_size = 0
    for secname in section_type:
        if re.search('\*', secname):
            secname = fnmatch.translate(secname)        # Translate glob-style wildcards into regex
        for aline in mem_sizes.splitlines():
            try:
                secline_matched = False
                # For libraries, there is an extra line of output that needs to be parsed
                secline = re.sub(r"\):",r"",(re.sub(r".*ex ",r"",aline)))

                secline = secline.split()[0]
                if secline == secname:              # check for exact match
                    cum_size += int(aline.split()[1])
                elif re.search('\*', secname):      # else check for a wildcard
                    if re.match(secname, secline):
                        cum_size += int(aline.split()[1])
                        secline_matched = True

                # Suppress warnings if it was a wildcard match 
                for ww in wilds:
                    if re.match(ww, secline):
                        secline_matched = True

                # Check if the section name isn't a known one then warn that it needs to be explicitly added, otherwise
                # we won't know what type of section it is.
                if (secline not in ALL_SECTIONS and
                        secline not in IGNORE_SECTIONS and
                        secline != pname and
                        not secline_matched and
                        secline not in secname_not_found_list):
                    secname_not_found_list.append(secline)
                    print "secline",secline,"secname",secname,"fname",fname,"pname",pname

            except IndexError:
                pass
    return cum_size


def print_sorted(column, lis):
    colname = {0:'NAME', 1:'CODE', 2:'CAL', 3:'CONST', 4:'RAM'}
    if column == 0:
        rev = False
    else:
        rev = True

    print
    print
    print "==============================================================================================================================="
    print "%70s" % ('SORTED BY ' + colname[column])
    print "==============================================================================================================================="
    print "%60s %10s %10s %10s %10s" % ('Name', 'Code', 'Cal', 'Const', 'RAM')
    lis.sort(key = lambda field:field[column], reverse=rev)
    for i in lis:
        name  = i[0]
        code  = i[1]
        cal   = i[2]
        const = i[3]
        ram   = i[4]
        print "%60s %10d %10d %10d %10d" % (name, code, cal, const, ram)

def help():
    print "Usage: memory_used.py [OPTION] [MAPFILE]"
    print "Prints out memory usage information for DW10F in decimal bytes"
    print "If a mapfile name is not provided it will try to find one in the current directory"
    print
    print "     -h, --help           print this help message"
    print "     -v, --verbose        give more detailed information"
    print "     -o, --org            ROM usage by organization"
    print "     -u, --unit           analyse each compilation unit"
    print "     -d, --debug          print debug info"
    print
    print "EXAMPLES"
    print "     memory_report.py                Print summary using first map file found"
    print "     memory_report.py other.map      Print summary using specified map file"
    print "     memory_report.py -v -o          Print detailed report, showing how much each organization uses"
    print "     memory_report.py -u             Print how much each object uses (mutually exclusive option)"

if __name__ == "__main__":
    main()
