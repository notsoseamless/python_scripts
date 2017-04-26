#To run the script
#go to gill_vob\6_coding folder through command prompt and then run
#..\..\tcg_cots_tool_vob\python\Python26\python26.exe ..\..\tcg_misc_tool_vob\sw_team_leader_tools\Creta_a2l_entry_creator.py {A2L PATH}
import re,os
import time
import subprocess,shutil,sys
import pyodbc
from os.path import exists
from subprocess import Popen,PIPE
import os.path
import tempfile
from functools import partial
import pywintypes
import win32com.client
import threading
import csv
import win32file
import traceback

######################################
# Constants
######################################
CHAR_MEAS_POS = 3
IN_MEAS_POS = 4
OUT_MEAS_POS = 5
LOC_MEAS_POS = 6


# SessionType Constants
CQ_SHARED_SESSION          = 1
CQ_PRIVATE_SESSION         = 2
CQ_ADMIN_SESSION           = 3
CQ_SHARED_METADATA_SESSION = 4

# BoolOp Constants
CQ_BOOL_OP_AND = 1
CQ_BOOL_OP_OR  = 2

# CompOp Constants
CQ_COMP_OP_EQ          = 1
CQ_COMP_OP_NEQ         = 2
CQ_COMP_OP_LT          = 3
CQ_COMP_OP_LTE         = 4
CQ_COMP_OP_GT          = 5
CQ_COMP_OP_GTE         = 6
CQ_COMP_OP_LIKE        = 7
CQ_COMP_OP_NOT_LIKE    = 8
CQ_COMP_OP_BETWEEN     = 9
CQ_COMP_OP_NOT_BETWEEN = 10
CQ_COMP_OP_IS_NULL     = 11
CQ_COMP_OP_IS_NOT_NULL = 12
CQ_COMP_OP_IN          = 13
CQ_COMP_OP_NOT_IN      = 14

# FetchStatus Constants
CQ_SUCCESS           = 1
CQ_NO_DATA_FOUND     = 2
CQ_MAX_ROWS_EXCEEDED = 3

SPEC_PATTERNS = [
    re.compile(r"^(B851\d{4})_(\d+\.\d+)$"),
    re.compile(r"^(R65[1238]\d{4})_(\d+\.\d+)$"),
    re.compile(r"^(B845\d{4})_(\d+\.\d+)$"),
]

BLOIS_BRANCH_PATTERNS = frozenset([
    re.compile(r"^(?:L|V|C)\d{2}_\d{2}$"),
    re.compile(r"^main$"),
    re.compile(r"^P\d{4}$"),
    re.compile(r"^AT_.+$"),
    re.compile(r"^FIE_\d{2}$"),
    re.compile(r"^VMA$"),
])

######################################
# Globals
######################################
#ConfigDictionary - A dictionary which Contain Information about project configuration
#ConfigDictionary[CONFIG] = {VALUE}

ConfigDictionary = {}



# Module Dictionary - A dictionary which contain path, spec number, measurement variables
# the template for this dictionary is
# ModuleDictionary[MODULE_NAME] = {(MODULE_PATH),(CODING_METHOD),[(CTAGS_FILE_PATH),
#(SPEC_NUMBER)_(SPEC_VERSION)],[(CHARACTERISTIC_MEAS)],[(OUTPUT_MEAS)],[(INPUT_MEAS)],[(LOCAL_MEAS)]}

ModuleDictionary  = {}

# Master Dictionary - A dictionary which contains all information about each specification
# in PCR
# the template for this dictionary is
# MasterDictionary[SPEC_NUMBER] = {[(CURR_BL_PCR_SPEC_VER),(PREV_BL_PCR_SPEC_VER),(SW_SPEC_VER)],
#(PCR_SPEC_DESC),(INDICATOR_CHG),[(CHARACTERISTIC_MEAS)],[(OUTPUT_MEAS)],[(INPUT_MEAS)],[(LOCAL_MEAS)]}

MasterDictionary = {}
REF_INDICATOR_FILEPATH = r"..\..\gill_vob\6_coding\A2l_Indicator_Of_Spec_Change.txt"

class A2l:
    '''
    Reads the A2l and create a dictionary based on the functionality
    '''
    from collections import defaultdict
    A2lDictionary = defaultdict( list )

    def __init__( self, a2l_path ):
        print 'preparing A2l Dictionary - NEW'
        pattern = re.compile(
            r'/begin (MEASUREMENT|CHARACTERISTIC|AXIS_PTS)[\s\c]*(.*?)\s.*?/end \1'
          , re.MULTILINE | re.DOTALL )
        with open( a2l_path ) as f_in:
            file_text = f_in.read()
            for match in re.findall( pattern, file_text ):
                self.A2lDictionary[ match[1][:7] ].append( match[1] )


class Ctags:
    """This class generates the ctags file by parsing the c file"""

    def __init__(self):
        self.infile = 'config.py'
        self.getListOfModules(self.getAutoCodeModuleList())

    def prepareCtagsDir(self):
        if not exists(r"..\..\gill_vob\6_coding\Ctags"):
            os.makedirs(r"..\..\gill_vob\6_coding\Ctags")

    def getAutoCodeModuleList(self):
        auto_code_module_list = []
        for line in open(self.infile):
            line = line.strip()
            if re.match("ModelFile",line):
                model_path = line.split("'")[1]
                if exists(model_path):
                    auto_code_module_list.append (re.sub("_autocode.mdl","",model_path.split("model/")[1]))
                else:
                    pass # prepare this list later - SK
        return auto_code_module_list

    def getListOfModules(self,ac_module_list ):
        self.prepareCtagsDir()
        exclude_module_list = ['F_M_Fault']
        for line in open(self.infile):
            line = line.strip()
            if re.match("SourceFile",line):
                path = line.split("'")[1]
                if not re.search("rtw/",path):
                    module_name = re.sub("\.c","",path.split("src/")[2])
                    ctags = False
                    if module_name not in exclude_module_list:
                        if module_name in ac_module_list:
                            mode = "AUTO"
                        else:
                            mode = "MANUAL"
                        tag_path = r"..\..\gill_vob\6_coding\Ctags\\"+module_name+r".ctags"
                        ModuleDictionary[module_name] = (path,mode,[tag_path,""],[],[],[],[])

    def genCtagsOutput(self):
        self.prepareCtagsDir()
        print "Number of modules : %d" %(len(ModuleDictionary.keys()))
        threads = []
        for module in ModuleDictionary.keys():
            thread = threading.Thread(target= partial(self.genCtagsFiles,module))
            thread.start()
            threads.append(thread)
            if (threading.activeCount() > 4):
                for t in threads:
                    t.join()
                threads = []
        if threads != []:
            for t in threads:
                t.join()
            threads = []

    def genCtagsFiles(self,module):
        tool = r"..\..\tcg_cots_tool_vob\gnu\ctags.exe"
        opt_fr = r"--language-force=c -x --c-types=+vx-pfcdefgmnstu --regex-C=/REPORT_FAULT_STATUS\\(.(.+_((CFG)|(cfg))),/\\1/,fault_read/"
        funcList = ['F_M_Record_Fault','F_M_Record_Var_Fault','F_M_Record_Fault_Mode6',
                    'F_M_Record_Fault_Mode6_Min_All','F_M_Record_Fault_Mode6_Max_All',
                    'F_M_Record_Var_Fault_Mode6','F_M_Record_Var_Flt_Mode6_Min_All',
                    'F_M_Record_Var_Flt_Mode6_Max_All','F_M_Record_Fault_Mode6_2_Tid',
                    'F_M_Record_Var_Fault_Mode6_2_Tid','F_M_Record_Fault_Mode6_3_Tid',
                    'F_M_Record_Var_Fault_Mode6_3_Tid']
        opt_fs = ""
        for func in funcList:
            opt_fs += r"--regex-C=/"+str(func)+r"\\(.(.+)\[G,\]/\\1/,fault_set/ "
        funcList = ['F_M_Record_No_Fault','F_M_Record_Var_No_Fault','F_M_Record_No_Fault_Mode6',
                    'F_M_Record_No_Flt_Mode6_Min_All','F_M_Record_No_Flt_Mode6_Max_All',
                    'F_M_Record_Var_No_Fault_Mode6','F_M_Record_Var_No_Flt_Mod6MinAll',
                    'F_M_Record_Var_No_Flt_Mod6MaxAll','F_M_Record_No_Fault_Mode6_2_Tid',
                    'F_M_Record_Var_No_Flt_Mod6_2_Tid','F_M_Record_No_Fault_Mode6_3_Tid',
                    'F_M_Record_Var_No_Flt_Mod6_3_Tid']
        opt_frs = ""
        for func in funcList:
            opt_frs += r"--regex-C=/"+str(func)+r"\\(.(.+)\[G,\]/\\1/,fault_reset/ "
        opt_fg = r"--regex-C=/F_M_Report_Fault_Group_Status\\(.(.+_((CFG)|(cfg)|(CFG\\[.+\\]))),/\\1/,fault_group_read/ --regex-C=/(F_M_[a-zA-Z0-9_]+)_GET_FG_ST_V1\\(\\)/\\1_FLT_GRP_CFG/,fault_group_read/"
        opt_ci = r"--regex-C=/\\((.+_NN_CFG)/\\1/,c_i_map/"

        # Check coding method Autocoded/Manual coded.
        if ModuleDictionary[module][1] == "AUTO":
            src_hdr = re.sub("\.c","",ModuleDictionary[module][0])+"_private.h"
        else:
            src_hdr = ""
        cmd = " ".join([tool,opt_fr,opt_fs,opt_frs,opt_fg,opt_ci,ModuleDictionary[module][0],src_hdr])
        process = Popen(cmd, stdout =PIPE)
        FILEPTR = open(ModuleDictionary[module][2][0],'w')
        FILEPTR.write(process.communicate()[0])
        FILEPTR.close()
class Pcr:
    """
     Class to extract the data from PCR database
    """
    def __init__(self,custinfo):
        ''' Initialise the variables '''
        self.swlabel = None
        self.element = None
        self.curpcrlabel = None
        self.preswlabel = None
        self.preelement = None
        self.prepcrlabel = None
        self.removed_specs = dict()
        self.pcrspecdictionary = {}
        self.custinfo = custinfo

    def extractPcrData(self):
        print "Preparing CURRENT PCR Label"
        mode = "AUTO"
        info_string = ("Note:You could bypass the function list generation"
                        " using the command \"BYPASS_FUNC_LIST\"")
        errormessage = "Current pcr label auto detection failed"
        correct_label_found = False
        while correct_label_found == False:
            try:
                curpcrdictionary = self.readCurrPcrLabel(mode)
            except:
                print errormessage
                print "Please manually enter the current SW label which is available in PCR (Ex.1FJCBAPP_B150P07): "
                print info_string
                self.swlabel= raw_input()
                # Option to Bypass the function list generation
                if self.swlabel.strip() == "BYPASS_FUNC_LIST":
                    sys.exit("A2L Function list generation bypassed")
                mode,errormessage = ("MANUAL","The entered Label seems to be wrong.")
                self.element = None
                print 40*"_"
            else:
                correct_label_found = True

        print "Preparing PREVIOUS PCR Label"
        mode,errormessage = ("AUTO","Previous pcr label auto detection failed")
        correct_label_found = False
        while correct_label_found == False:
            try:
                prepcrdictionary = self.readPreviousPcrLabel(mode)
            except:
                print errormessage
                print "Please manually enter the previous SW Label which is available in PCR.(Ex.1FJCBAPP_B150P07):"
                print info_string
                self.preswlabel = raw_input()
                # Option to Bypass the function list generation
                if self.preswlabel.strip() == "BYPASS_FUNC_LIST":
                    sys.exit("A2L Function list generation bypassed")
                mode,errormessage = ("MANUAL","The entered Label seems to be wrong.")
                self.element = None
                print 40*"_"
            else:
                correct_label_found = True

        self.pcrspecdictionary = self.compareSpecsofDiffPcrLabel(curpcrdictionary,
                                                                prepcrdictionary)

    def readCurrPcrLabel(self,mode):
        if(mode == "AUTO"):
            self.swlabel,self.element = self.getLabelName(self.custinfo)
            if ConfigDictionary["CURR_SW_LABEL"] != "DEFAULT":
                self.swlabel = ConfigDictionary["CURR_SW_LABEL"]
        self.curpcrlabel = self.preparePcrLabel(self.swlabel,self.custinfo)
        curpcrdictionary = dict()
        self.curpcrlabel, curpcrdictionary = self.retriveDatasfromPcr(self.curpcrlabel)
        return curpcrdictionary

    def readPreviousPcrLabel(self,mode):
        if(mode == "AUTO"):
            if ConfigDictionary["PRE_SW_LABEL"] == "DEFAULT":
                self.preswlabel,self.preelement = self.getPreviousLabel(self.swlabel,
                                                      self.element,self.custinfo)
            else:
                self.preswlabel = ConfigDictionary["PRE_SW_LABEL"]
        try:
            reflabel = self.getRefIndBaseline()
            if len(reflabel.replace(self.custinfo,"")) > 4:
                actrefbaseline = int(reflabel.replace(self.custinfo,"")[:-3])
            else:
                actrefbaseline = int(reflabel.replace(self.custinfo,""))
            if len(self.preswlabel.replace(self.custinfo,"")) > 4:
                actpreswbaseline = int(self.preswlabel.replace(self.custinfo,"")[:-3])
            else:
                actpreswbaseline = int(self.preswlabel.replace(self.custinfo,""))
            if (actrefbaseline >= actpreswbaseline):
                if mode == "AUTO":
                    self.preswlabel = reflabel
                else:
                    if reflabel != self.preswlabel:
                        print "Warning:The entered previous baseline label seems bit old"
                        print " it uses the reference indicator baseline %s " %(reflabel)
            else:
                print "Warning:Refernce Indicator of change to be updated to %s" %(self.preswlabel)
                print "This build uses reference Indicator for baseline %s" %(reflabel)
        except:
            pass
        self.prepcrlabel = self.preparePcrLabel(self.preswlabel,self.custinfo)
        prepcrdictionary = dict()
        self.prepcrlabel, prepcrdictionary = self.retriveDatasfromPcr(self.prepcrlabel)
        return prepcrdictionary

    def getRefIndBaseline(self):
        """ Get the Baseline used to calculate the reference indicator """
        line = [line for line in open(REF_INDICATOR_FILEPATH)
                                            if line.find("Baseline")!= -1 ]
        return line[0].replace("#","").strip().split(":")[1]

    def createShelveDb(self):
        import shelve
        md = shelve.open(r"..\..\gill_vob\6_coding\Ctags\ModDict.db")
        try:
            for module in ModuleDictionary.keys():
                md[module] = ModuleDictionary[module]
        finally:
            md.close()
        pd = shelve.open(r"..\..\gill_vob\6_coding\Ctags\PcrDict.db")
        try:
            for spec in self.pcrspecdictionary.keys():
                try:
                    pd[str(spec)] = self.pcrspecdictionary[spec]
                except:
                    print "The spec %s has issues" %(spec)
        finally:
            md.close()

    def readShelveDb(self):
        import shelve
        md = shelve.open(r"..\..\gill_vob\6_coding\Ctags\ModDict.db")
        try:
            for module in md.keys():
                ModuleDictionary[module] = md[module]
        finally:
            md.close()

    def compareSpecsofDiffPcrLabel(self,dict1 = {},dict2 = {}):
        pcrdatabase = {}
        for spec in dict1.keys():
           pcrdatabase[spec] = ([dict1[spec][0],''],dict1[spec][1],dict1[spec][2],dict1[spec][3])
        for spec in dict2.keys():
            if spec not in pcrdatabase.keys():
                pcrdatabase[spec] = (['',dict2[spec][0]],dict2[spec][1],dict2[spec][2],dict2[spec][3])
                self.removed_specs[spec] = (dict2[spec][0],dict2[spec][1])
            else:
                pcrdatabase[spec][0][1] = dict2[spec][0]
        return pcrdatabase

    def preparePcrLabel(self,label,custinfo):
        ''' SW Label format doesnot match the PCR Label in some cases. Hence
            prepare the correct PCR Label '''
        temp = label.replace(custinfo,"")
        if temp[0] != '0':
            if len(temp)== 4:
                baseline = temp[:4]
                phase = 'D00'
            else:
                baseline = temp[:3]
                phase = temp[3:]
        else:
            if len(temp)== 4:
                baseline = temp[1:4]
                phase = 'D00'
            else:
                baseline = temp[1:4]
                phase = temp[4:]
        ver = '1'
        pcrlabel = custinfo+baseline+phase+ver
        return pcrlabel

    def check_output(self, *popenargs, **kwargs):
        if 'stdout' in kwargs:
            raise ValueError('stdout argument not allowed, it will be overridden.')
        process = subprocess.Popen(stdout=subprocess.PIPE, *popenargs, **kwargs)
        output, unused_err = process.communicate()
        retcode = process.poll()
        if retcode:
            cmd = kwargs.get("args")
            if cmd is None:
                cmd = popenargs[0]
        return output

    def getLabelName(self,custinfo):
        elementname = Spec.getLinkPath("config.py")
        output = self.check_output('cleartool describe -fmt "%Sn" '+elementname, shell=True)
        if output.find("task_gv") != -1:
            elementlist = output.split("\\")
            elementlist[-1] = '0'
            element = elementname+'@@'+'\\'.join(elementlist)
            mainbubble = self.check_output('cleartool describe -fmt "%PSn" '+element, shell=True)
        else:
            mainbubble = output
        element = elementname+'@@'+mainbubble
        labelstring = self.check_output('cleartool describe -fmt "%l" '+element, shell=True)
        label = self.extratLabelInfo(labelstring,custinfo)
        return label,element

    def extratLabelInfo(self,labelstring,custinfo):
        labelstring = re.sub('[()]',"",labelstring)
        if re.search(', ',labelstring):
            labels = labelstring.split(', ')
            labelsCopy =  list(labels)
            for label in labelsCopy:
                if not re.search(custinfo,label):
                    labels.remove(label)
            labels.sort()
            templist = []
            for label in labels:
                temp = label.replace(custinfo,"")
                if not re.search('(P)|(GV)',temp):
                    templist.append(label)
            if templist == []:
                label = labels[-1]
            else:
                templist.sort()
                label = templist[-1]
        else:
            label = labelstring
        return label
    def prepareClearToolCommand(self, element):
        # Some config.py has branches which has to be handled
        if len(element.split("\\"))> 3:
            elementlist = element.split("@@")
            branch = elementlist[1][:elementlist[1].rfind("\\")]
            filename = elementlist[0]
            ct_comand = 'cleartool lsvtree -branch '+ branch+" -nr "+filename
        else:
            ct_comand = 'cleartool lsvtree -nr -a '+element
        return ct_comand

    def getPreviousLabel(self,curlabel,element,custinfo,pcrlabel_notfound=False):
        labellist = []
        ct_comand = self.prepareClearToolCommand(element)
        output = self.check_output(ct_comand, shell=True)
        labellist = output.split('\n')
        curlabelfound = False
        while labellist:
            string = labellist.pop().strip()
            if string.find('(') != -1:
                labelstring = string[string.find('('):]
                label = self.extratLabelInfo(labelstring,custinfo)
                if label == curlabel:
                    curlabelfound = True
                elif curlabelfound == True:
                    temp = label.replace(custinfo,"")
                    if False == pcrlabel_notfound:
                        #Previous label value should be previous release to customer
                        if temp[:2] != curlabel.replace(custinfo,"")[:2]:
                            if not re.search('(P)|(GV)',temp) and label != 0:
                                previouselement = string.split()[0]
                                previouslabel = label
                                return previouslabel,previouselement
                    else:
                        previouselement = string.split()[0]
                        previouslabel = label
                        return previouslabel,previouselement
            else:
                pass
        return "ERROR:Label not found"


    def retriveDatasfromPcr(self,labelname):
        specdictionary = {}
#        conn = pymssql.connect(host='dlbw72t2j\clearquest', user='guest', password='guest', database='DB_SAM')
#        cur = conn.cursor()
        orig_name = labelname
        cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER=FRBLO-DB04;DATABASE=DB_SAM;UID=BloisElectronic;PWD=Blois1@#$%')
        cur = cnxn.cursor()
        
        connectionstring = """SELECT o_reference, specversion, o_title, o_category, SPC_LABEL
                    FROM
                    (
                    SELECT
                    SPC_SHORT_LABEL AS o_category, 
                    TB_SPEC.SPV_REFERENCE_FK AS o_reference,
                    CONVERT(VARCHAR(10), CAST(SPV_VERSION AS DECIMAL(38,1))) AS specversion,
                    CONVERT(VARCHAR(10), CAST(o_maxversionT AS DECIMAL(38,1))) AS specversionMax, 
                    SPV_TITLE AS o_title,
                    (user1.USR_LAST_NAME+' '+user1.USR_FIRST_NAME) AS o_author,
                    (user2.USR_LAST_NAME+' '+user2.USR_FIRST_NAME) AS o_approver,
                    child.PSP_PRIORITY AS o_priority,
                    SPC_LABEL,
                    CONVERT(CHAR(10),SPV_DATE,110) AS FormatDate,
                    CASE WHEN CONF_LEVEL IS NULL THEN 
                    (CASE WHEN SPR_CONFIDENTIALITY=0 THEN 'Confidential' ELSE 'Not Confidential' END)
                    WHEN CONF_LEVEL=1 THEN 'Confidential' ELSE 'Not Confidential' END AS o_confidentiality,
                    child.PSP_COMMENT AS o_comment,
                    SPR_CONFIDENTIALITY+1 AS GenConf,
                    CONF_LEVEL AS CustomConf
                    FROM TB_PACKAGE_SPECIFICATIONS AS child
                    INNER JOIN TB_PACKAGES ON PSP_PACK_FK=PCK__PK AND PCK__PK=(
                    SELECT PCK__PK
                    FROM TB_PACKAGES
                    WHERE PCK_HARDWARE_FK+PCK_CUSTOMER_FK+PCK_SOFTWARE_FK+PCK_VARIANT+PCK_VERSION=?)
                    INNER JOIN TB_SPECIFICATION_VERSIONS AS TB_SPEC ON SPV__PK=PSP_SPEC_FK
                    LEFT OUTER
                    JOIN TB_PACKAGE_SPECIFICATIONS AS parent ON parent.PSP_PACK_FK=PCK_PARENT1_FK AND parent.PSP_SPEC_FK=child.PSP_SPEC_FK
                    INNER JOIN (
                    SELECT DISTINCT SPV_REFERENCE_FK, MAX(SPV_VERSION) AS o_maxversionT
                    FROM TB_SPECIFICATION_VERSIONS
                    GROUP BY SPV_REFERENCE_FK) AS TBMAX ON TBMAX.SPV_REFERENCE_FK=TB_SPEC.SPV_REFERENCE_FK
                    INNER JOIN TB_SPECIFICATION_REFERENCES ON SPR__PK=TB_SPEC.SPV_REFERENCE_FK
                    INNER JOIN TB_SPECIFICATION_CATEGORIES ON SPR_CATEGORY_FK=SPC__PK
                    INNER JOIN TB_USERS AS user1 ON user1.USR__PK=SPV_AUTHOR_FK
                    INNER JOIN TB_USERS AS user2 ON user2.USR__PK=SPV_APPROVER_FK
                    LEFT OUTER
                    JOIN TB_SPECIFICATION_CONFIDENTIALITY ON SPV__PK=CONF_SPECINDEX AND PCK_CUSTOMER_FK COLLATE SQL_Latin1_General_CP1250_CI_AS=CONF_CUSTINDEX
                    UNION
                    SELECT
                    CONVERT(NVARCHAR(100),SWC_.swc_title+' '+SWC_.swc_reference+' '+SWC_.swc_version) COLLATE SQL_Latin1_General_CP1250_CI_AS AS o_category,
                    spec.d_number COLLATE SQL_Latin1_General_CP1250_CI_AS AS o_reference,
                    CONVERT(VARCHAR(10),spec.d_version) COLLATE SQL_Latin1_General_CP1250_CI_AS AS specversion,
                    CONVERT(VARCHAR(10),
                    CONVERT(VARCHAR(10),
                    CAST((TBMAX.o_maxversionT/1000) AS DECIMAL(38,0))) + '.'+ CONVERT(VARCHAR(10),
                    (TBMAX.o_maxversionT - (TBMAX.o_maxversionT/1000)*1000))) COLLATE SQL_Latin1_General_CP1250_CI_AS AS specversionMax,
                    CONVERT(NVARCHAR(300),spec.d_title) COLLATE SQL_Latin1_General_CP1250_CI_AS AS o_title,
                    Author.name COLLATE SQL_Latin1_General_CP1250_CI_AS AS o_author,
                    Approver.name COLLATE SQL_Latin1_General_CP1250_CI_AS AS o_approver,
                    child.PSWC_PRIORITY AS o_priority,
                    CONVERT(NVARCHAR(100),SWC_.swc_title+' '+SWC_.swc_reference+' '+SWC_.swc_version) COLLATE SQL_Latin1_General_CP1250_CI_AS AS SPC_LABEL,
                    CONVERT(CHAR(10),spec.spec_approveddate,110) AS FormatDate,
                    CASE WHEN CONF_LEVEL IS NULL THEN 
                    (CASE WHEN SPR_CONFIDENTIALITY=0 THEN 'Confidential' ELSE 'Not Confidential' END)
                    WHEN CONF_LEVEL=1 THEN 'Confidential' ELSE 'Not Confidential' END AS o_confidentiality,
                    child.PSWC_COMMENT COLLATE SQL_Latin1_General_CP1250_CI_AS AS o_comment,
                    SPR_CONFIDENTIALITY+1 AS GenConf,
                    CONF_LEVEL AS CustomConf
                    FROM TB_PACKAGE_SWC AS child
                    INNER JOIN TB_PACKAGES ON PCK__PK=(
                    SELECT PCK__PK
                    FROM TB_PACKAGES
                    WHERE PCK_HARDWARE_FK+PCK_CUSTOMER_FK+PCK_SOFTWARE_FK+PCK_VARIANT+PCK_VERSION=?) AND child.PSWC_PACK_FK=PCK__PK
                    INNER JOIN CQGlobal.CQGlobal_dbo.swc AS SWC_ ON PSWC_SWC_FK=SWC_.dbid
                    LEFT OUTER
                    JOIN CQGlobal.CQGlobal_dbo.parent_child_links AS SWC_2childSWC ON SWC_.dbid= SWC_2childSWC.parent_dbid AND 16782535 = SWC_2childSWC.parent_fielddef_id
                    LEFT OUTER
                    JOIN CQGlobal.CQGlobal_dbo.swc AS childSWC ON SWC_2childSWC.child_dbid = childSWC.dbid AND SWC_.dbid <>0
                    INNER JOIN CQGlobal.CQGlobal_dbo.parent_child_links AS Spec2Swc ON ((SWC_.dbid = Spec2Swc.parent_dbid AND SWC_.dbid<>0) OR (childSWC.dbid = Spec2Swc.parent_dbid AND childSWC.dbid<>0)) AND 16782536 = Spec2Swc.parent_fielddef_id
                    INNER JOIN CQGlobal.CQGlobal_dbo.spec AS spec ON Spec2Swc.child_dbid = spec.dbid AND spec.dbid<>0
                    INNER JOIN TB_SPECIFICATION_VERSIONS AS TB_SPEC ON CONVERT(VARCHAR(15),spec.d_number COLLATE SQL_Latin1_General_CP1250_CI_AS)= CONVERT(VARCHAR(15),TB_SPEC.SPV_REFERENCE_FK) AND CONVERT(VARCHAR(10), CAST((spec.d_version) AS DECIMAL(38,1)))= CONVERT(VARCHAR(10), CAST((SPV_VERSION) AS DECIMAL(38,1)))
                    INNER JOIN TB_SPECIFICATION_REFERENCES ON SPR__PK=TB_SPEC.SPV_REFERENCE_FK
                    LEFT OUTER
                    JOIN DB_SAM.dbo.TB_SPECIFICATION_CONFIDENTIALITY ON SPV__PK=CONF_SPECINDEX AND PCK_CUSTOMER_FK=CONF_CUSTINDEX COLLATE SQL_Latin1_General_CP1250_CI_AS
                    LEFT OUTER
                    JOIN (
                    SELECT MAX(spec_versionint) AS o_maxversionT,d_number
                    FROM CQGlobal.CQGlobal_dbo.spec AS spec2
                    GROUP BY d_number) AS TBMAX ON TBMAX.d_number=spec.d_number
                    INNER JOIN CQGlobal.CQGlobal_dbo.hresource AS Author ON spec.spec_author=Author.dbid
                    INNER JOIN CQGlobal.CQGlobal_dbo.hresource AS Approver ON spec.spec_approver=Approver.dbid) AS T1
                    ORDER BY T1.o_category, T1.o_reference"""
 
        cur.execute(connectionstring,labelname,labelname)
        row = cur.fetchone()
        while row:
            specdictionary[row[0].strip()] = (round(float(row[1]),2),row[2],row[3],row[4])
            row = cur.fetchone()
        if specdictionary == {}:
            print "PCR Label %s not found" %(labelname)
            labelname = labelname[:-1]+'2'
            cur.execute(connectionstring,labelname,labelname)
            row = cur.fetchone()
            while row:
                specdictionary[row[0].strip()] = (round(float(row[1]),2),row[2],row[3],row[4])
                row = cur.fetchone()
        cnxn.close()
        if specdictionary == {}:
            sys.exit("PCR label %s not found " %(orig_name))
        return labelname,specdictionary

class BloisCQConnection:
    __cq_session = None

    @staticmethod
    def connect():
        if not BloisCQConnection.__cq_session:
            cq_session = win32com.client.Dispatch("ClearQuest.Session")
            try:
                cq_session.UserLogon("guest", "guest", "bl_gs", CQ_PRIVATE_SESSION, "Blois")
            except:
                print 'Warning: Could not logon to CQ Connection "Blois"'
            BloisCQConnection.__cq_session = cq_session

        return BloisCQConnection.__cq_session


class SpecRefQuery:
    """Query Blois CQ for the reference and version of all specs associated with the specified file+version"""

    __cq_session = None
    __query_def = None

    @staticmethod
    def __class_init():
        if not SpecRefQuery.__cq_session:
            SpecRefQuery.__cq_session = BloisCQConnection.connect()

        cq_session = SpecRefQuery.__cq_session

        if not SpecRefQuery.__query_def:
            SpecRefQuery.__query_def = cq_session.BuildQuery("File")
            SpecRefQuery.__query_def.BuildField("Model.REF_Spec.Spec_Reference")
            SpecRefQuery.__query_def.BuildField("Model.REF_Spec.Spec_Version")
            SpecRefQuery.__query_def.BuildField("Model.REF_Spec.SPEC_Validity")

        query_def = SpecRefQuery.__query_def

        return (cq_session, query_def)

    def __init__(self, file_name, version):
        (cq_session, query_def) = SpecRefQuery.__class_init()
        self.filter_node = query_def.BuildFilterOperator(CQ_BOOL_OP_AND)
        self.filter_node.BuildFilter("FileName", CQ_COMP_OP_EQ, file_name)
        self.filter_node.BuildFilter("CcVersionIntegrated", CQ_COMP_OP_EQ, version)
        self.result_set = cq_session.BuildResultSet(query_def)
        self.result_set.Execute()

    def __iter__(self):
        fetch_status = self.result_set.MoveNext
        while fetch_status == CQ_SUCCESS:
            spec_reference = self.result_set.GetColumnValue(1)
            spec_version   = self.result_set.GetColumnValue(2)
            spec_validity  = self.result_set.GetColumnValue(3)
            yield (spec_reference, spec_version, spec_validity)
            fetch_status = self.result_set.MoveNext



class Spec:
    def __init__(self):
        pass

    def getSpecNbrfromSpecBranch(self,module,log= None):
        version = 'None'
        spec_nbr_fnd = False
        path = Spec.getLinkPath(ModuleDictionary[module][0],log) #get proper name if it's a link
        cmd = 'cleartool describe -fmt "%Vn" ' + path
        p = subprocess.Popen(cmd,shell = False,stdin = subprocess.PIPE,
                           stdout = subprocess.PIPE,stderr = subprocess.STDOUT)
        version = p.stdout.read()
        retval = p.wait()
        if not retval == 0:
            if not log == None:
                log.ERRLOG('problem getting version',cmd,version)
        m = re.sub(r"\\main\\","",version)
        if (m != ''):
            if(re.search(r"\\",m)):
                m = m.split("\\",2)
                if re.search("[RAB]\d",m[0].upper()):
                    ModuleDictionary[module][2][1] = m[0]
                    spec_nbr_fnd = True
                else:
                    #print "Spec branch %s is not spec number" %(m[0])
                    pass
        return spec_nbr_fnd

    def getSpecNbrfromClrCaseAttribute(self,module):
        spec_nbr_fnd = False
        specnbr = self.readClrCaseAttribute(ModuleDictionary[module][0],"tcgSpecInfo")
        specnbr =specnbr.strip()
        if(re.search("\"", specnbr)):
            specnbr = re.sub("\"","",specnbr)
        if specnbr == "":
            specnbr = self.readClrCaseAttribute(ModuleDictionary[module][0],"tcgSpecInfo_tci")
            specnbr =specnbr.strip()
            if(re.search("\"", specnbr)):
                specnbr = re.sub("\"","",specnbr)
        if specnbr != "":
            ModuleDictionary[module][2][1] = specnbr
            spec_nbr_fnd = True
        return spec_nbr_fnd

    def getSpecNbrfromTable(self,module):
        return Table().getSpecNbrfromTable(module)

    def readClrCaseAttribute(self,path,attname,log =None):
        retfile = Spec.getLinkPath(path,log) #get proper name if it's a link
        cmd = 'cleartool describe -fmt "%['+ attname +']NSa" ' + retfile
        p = subprocess.Popen(cmd,shell = False, stdin = subprocess.PIPE,
                           stdout = subprocess.PIPE,stderr = subprocess.STDOUT)
        lines = p.stdout.read()
        retval = p.wait()
        attr = ''
        if not retval == 0:
            if not log == None:
                log.ERRLOG('problem getting attribute',cmd,lines)
        else:
            attr = lines
        if not attr == '':
            attrarr = attr.split()
            return attrarr.pop()
        else:
            return attr

    @staticmethod
    def getLinkPath(file,log = None):
        """ if file is a link, return linkpath """
        cmd = 'cleartool ls -l ' + file
        p = subprocess.Popen(cmd, shell = False, stdin = subprocess.PIPE,
                           stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
        lines = p.stdout.read()
        retval = p.wait()
        filen = ''
        if not retval == 0:
            filen = ''
        elif 'view private file' in lines:
            filen = ''
        else:
            filen = file

        if not filen == '':
            cmd = 'cleartool desc -fmt %[slink_text]p ' + filen
            p = subprocess.Popen(cmd,shell = False, stdin = subprocess.PIPE,
                           stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
            lines = p.stdout.read()
            retval = p.wait()
            if lines == '': #this is not a link
                return(filen)
            else:
                cpath = os.path.dirname(filen)
                relpath = lines.rstrip()
                return(os.path.join(cpath,relpath))
        else:
            if not log == None:
                log.ERRLOG('file not under clearcase',cmd,lines)
            return filen

    def get_spec_info_from_labels(self,version):
        specs = set()
        for label in version.Labels:
            label_name = label.Type.Name
            for spec_pattern in SPEC_PATTERNS:
                m = spec_pattern.match(label_name)
                if m:
                    (spec_reference, spec_version) = m.group(1, 2)
                    specs.add((spec_reference, spec_version))
                    break

        return specs

    def get_spec_info_from_blois_CQ(self,version):

        specs = set()
        branch_name = version.Branch.Type.Name
        file_name = os.path.basename(version.Element.Path)

        for branch_pattern in BLOIS_BRANCH_PATTERNS:
            if branch_pattern.match(branch_name):
                cq_results = SpecRefQuery(file_name, version.Identifier)

                for (spec_ref, spec_ver, spec_validity) in cq_results:
                    if spec_ref and spec_ver and all([word.isdigit() for word in spec_ver.split(".", 1)]):
                        specs.add((spec_ref, spec_ver))
                        # Cache the spec validity data for later
                        #spec_validity_cache[(spec_ref, spec_ver)] = spec_validity


                break

        return specs

    def getSpecNbrfromImpleData(self,module,pcrdata,IClearCase):
        spec_found = False
        spec_number = 0
        spec_version = 0
        autogen_module = ['dti','dti_iso_sub','s_s_scheduler','F_M_Fault']
        if module not in autogen_module:

            file_path = ModuleDictionary[module][0]
            try:
                real_path = Spec.getLinkPath(file_path)
                real_path = real_path.replace('/','\\')
                element = IClearCase.Element(real_path)
                this_file_implements = set()
                # Get any spec info from labels applied to the version.
                this_file_implements.update( self.get_spec_info_from_labels(element.Version))
                # Get any spec info from Blois CQ
                this_file_implements.update(self.get_spec_info_from_blois_CQ(element.Version))

                this_file_implements = sorted(this_file_implements)
                if len(this_file_implements) > 0:
                    spec_found = True
                    for (number,ver) in this_file_implements:
                        if len(this_file_implements) == 1 :
                            spec_number = number
                            spec_version = ver
                        else:
                            if spec_number == 0:
                                spec_number = number
                            elif spec_number == number:
                                spec_version = max(ver,spec_version)
                            else:
                                if spec_number not in pcrdata.keys():
                                    if number in pcrdata.keys():
                                        spec_number = number
                                        spec_version = ver
                                    else:
                                        spec_number = number
                                        spec_version = ver
                                        break
                    ModuleDictionary[module][2][1] = str(spec_number)+"_"+str(spec_version)
            except:
                #print file_path
                pass
        return spec_found


    def updateSpecnbrMasterDictionary(self,pcrdata):
        IClearCase = win32com.client.Dispatch("ClearCase.Application")
        threads = []
        count = 0
        tot_modules = len(ModuleDictionary.keys())
        for module in ModuleDictionary.keys():
            print "Gathering Spec numbers: %d%% complete\r" % int(round(float(count) /tot_modules  * 100)),
            self.findSpecNumbers(module,pcrdata,IClearCase)
            count +=1

    def findSpecNumbers(self,module,pcrdata,IClearCase):
        if self.getSpecNbrfromSpecBranch(module):
            pass
        elif self.getSpecNbrfromClrCaseAttribute(module):
            pass
        elif self.getSpecNbrfromImpleData(module,pcrdata,IClearCase):
            pass
        else:
            self.getSpecNbrfromTable(module)


class MeasVar:
    VarNotAddedToFuncList = []
    C_I_Maps =[]
    def __init__(self):
        self.objfunclistmodule = r'src\appli\c_i\src\c_i_fault_objcode_func_list.a2l'

    def updateCalibration(self, string, list,mname):
        patt = "(CAL )|(_APT)|(_GRP_FLT_APV)|(_DFC_APV)|(_LIM_APV)|(F_M_FREEZE_FRAME_DATA_ID_APV)"
        if (re.search(patt,string) or
            (re.search('M_MAP',string) and (not re.search('F_M_MAP',string)))):
                var = string.split()[0]
                var_fnd = True
                if not (re.search('EXTERN',string,re.IGNORECASE) and
                    not re.search('_EXTERN',string,re.IGNORECASE)):
                    if not re.search('c_i_maps',mname):
                        pattern  = str(var.upper())+"$|"+str(var.upper())+"_(\d)*$|"\
                            +str(var.upper())+"\.|"+str(var.upper())+"_(\d)*\."
                        self.searchA2lDictionary(var.upper(),list,pattern)
                    elif re.search('_APV',var):
                        self.C_I_Maps.append(var)
                    else:
                        pass
                elif var in self.C_I_Maps:
                    pattern  = str(var.upper())+"$|"+str(var.upper())+"_(\d)*$|"+\
                                    str(var.upper())+"\.|"+str(var.upper())+"_(\d)*\."
                    self.searchA2lDictionary(var.upper(),list,pattern)
                else:
                    pass
        else:
            var_fnd = False
        return var_fnd

    def updateLocMeasurement(self,string,list):
        if (re.search('variable',string) and re.search('static',string,re.IGNORECASE)):
            var = string.split()[0]
            pattern  = str(var)+"$|"+str(var)+"_(\d)*$|"+str(var)+"\.|"+str(var)+"_(\d)*\."
            self.searchA2lDictionary(var,list,pattern)
            var_fnd = True
        else:
            var_fnd = False
        return var_fnd

    def updateOutMeasurement(self,string,list):
        if (re.search('variable',string)):
            var = string.split()[0]
            # Deal with define CPV's use
            if re.match('CONST_',var) and re.search('_CPV',var):
                var = var.replace('CONST_',"")
                pattern  = str(var)+"$|"+str(var)+"_(\d)*$|"+str(var)+"\.|"+str(var)+"_(\d)*\."
                self.searchA2lDictionary(var,list,pattern)
            else:
                pattern  = str(var)+"$|"+str(var)+"_(\d)*$|"+str(var)+"\.|"+str(var)+"_(\d)*\."
                self.searchA2lDictionary(string.split()[0],list,pattern)
            var_fnd = True
        else:
            var_fnd = False
        return var_fnd

    def updateInMeasurement(self,string,list):
        if re.search("externvar",string):
            var = string.split()[0]
            pattern  = str(var)+"$|"+str(var)+"_(\d)*$|"+str(var)+"\.|"+str(var)+"_(\d)*\."
            self.searchA2lDictionary(var,list,pattern)
            var_fnd = True
        else:
            var_fnd = False
        return var_fnd

    def handleCIMaps(self,string,list):
        if (re.search(' c_i_map ',string)):
            strList = string.split()
            c_i_string = string[:string.find(" c_i_map")]
            c_i_string_arr= re.split("\W+", c_i_string)
            for temp in c_i_string_arr:
                if temp.find("_NN_CFG") != -1:
                    c_i_var = temp;
            var = c_i_var[:c_i_var.find("_NN_CFG")]
            pattern  = str(var)+"(_)"
            self.searchA2lDictionary(var,list,pattern)
            varlist = c_i_var.split("_")
            var = varlist[0]+"_"+varlist[1]+"_"+varlist[2]+"_"
            pattern  = "(MSK_APV)|(SL_APV)"
            self.searchA2lDictionary(var,list,pattern)
            var_fnd = True
        else:
            var_fnd = False
        return var_fnd

    def findSuppFaultsandArraysize(self,faultname):
        defaultlist = ['soft','rec']
        measlist = []
        suplist = []
        arraysize = 0
        var = faultname + "_fault_"
        pattern = ""
        self.searchA2lDictionary(var,measlist,pattern)
        for meas in measlist:
            sup = meas[len(var):]
            if re.match('flag',sup):
                arraysize +=1
            elif sup not in defaultlist:
                suplist.append(sup)
            else:
                pass
        if arraysize == 0:
            self.searchA2lDictionary(faultname,measlist,pattern)
            for meas in measlist:
                sup = meas[len(faultname):]
                if re.match('_flag',sup):
                    arraysize +=1
        return suplist,arraysize

    def createFltMeasListeachSuppChar(self,var,arraysize,appendlist):
        fltmeaslist = []
        for char in appendlist:
            if char != "":
                cal = 'APV.'+ char
            else:
                cal = 'INH_APV'
            fltmeaslist.append(var.upper()+'_'+cal)
        if arraysize > 1:
            for size in range(arraysize):
                for char in appendlist:
                    if char != "":
                        cal = 'APV_'+str(size)+'.'+ char
                    else:
                        cal = 'INH_APV_'+str(size)
                    fltmeaslist.append(var.upper()+'_'+cal)
        return fltmeaslist

    def createFltMeasListeachSuppOut(self,var,arraysize,appendlist):
        fltmeaslist = []
        for char in appendlist:
            if char == 'cnt':
                if arraysize == 1 or arraysize == 0:
                    fltmeaslist.append(var+'_cnt.dfctr')
                    fltmeaslist.append(var+'_cnt.rdnctr')
                else:
                    for size in range(arraysize):
                        fltmeaslist.append(var+'_cnt_'+str(size)+'.dfctr')
                        fltmeaslist.append(var+'_cnt_'+str(size)+'.rdnctr')
            else:
                fltmeaslist.append(var+'_'+char)
        return fltmeaslist

    def createFltMeasList(self,var,appendlist,supplementary,arraysize,method):
        fltmeaslist =[]
        if method == 'CHAR':
            if supplementary == []:
                fltmeaslist = self.createFltMeasListeachSuppChar(var,arraysize,appendlist)
            else:
                for sup in supplementary:
                    supvar = var+"_"+sup
                    fltmeaslist.extend(self.createFltMeasListeachSuppChar(supvar,arraysize,appendlist))
        else:
            if supplementary == []:
                fltmeaslist = self.createFltMeasListeachSuppOut(var,arraysize,appendlist)
                fltmeaslist.append(var+"_fault_flag")
            else:
                for sup in supplementary:
                    supvar = var+"_"+sup
                    fltmeaslist.extend(self.createFltMeasListeachSuppOut(supvar,arraysize,appendlist))
                    fltmeaslist.append(var+"_fault_"+sup)
                    fltmeaslist.append(var+"_fault_flag")
                    fltmeaslist.append(var+"_fault_soft")
                    fltmeaslist.append(var+"_fault_rec")
        return fltmeaslist

    def handleFaultManager(self,string,charlist,inlist,outlist):
        strList = string.split()
        obj_List = ['F_M_GEC', 'F_M_GED','F_M_GEM','F_M_TEC','F_M_TED','F_M_CET','F_M_CEA','F_M_CEN','F_M_CEP','F_M_CES','F_M_LML','F_M_LMV','F_M_VLC']
        charAppendList = ['CLASS','DFDEC','DFINC','DTC_HMB','DTC_LB','E_DATA_CLASS',
                                    'OCCURRENCE','READ','CONFIG_MASK','SAE_DTC',""]
        outAppendList = ['df','dbnc','cf','rdn','lcf','diag_en','inh','clf','scf','srdn','mf',
            'cnt','fault_rec','fault_soft','flag','sat','stdtc','min_nvv','max_nvv','val_nvv']
        supplementary =[]
        if re.search('fault_read ',string):
            var = string[:string.find("_FLT_CF")]
            # remove junk charaters
            var = var[var.find('F_M_'):]
            #  Check added, to support object code variables
            tempKey = var[:7]
            if tempKey not in obj_List:
                var = (var[:5].upper()+var[5:].lower())
            var = var + "_fault_flag"
            self.searchA2lDictionary(var,inlist,"")
            var_fnd = True
        elif re.search('fault_set ',string):
            var = string[:string.find("_FLT_CF")]
            # remove junk charaters
            var = var[var.find('F_M_'):]
            tempKey = var[:7]
            if tempKey not in obj_List:
                var = (var[:5].upper()+var[5:].lower())
            supplementary,arraysize = self.findSuppFaultsandArraysize(var)
            fltmeaslist = self.createFltMeasList(var,charAppendList,supplementary,arraysize,'CHAR')
            for measvar in fltmeaslist:
                self.searchA2lDictionary(measvar,charlist,"")
            fltmeaslist = self.createFltMeasList(var,outAppendList,supplementary,arraysize,'OUT')
            for measvar in fltmeaslist:
                self.searchA2lDictionary(measvar,outlist,"")
            var_fnd = True
        elif ((re.search('fault_reset ',string))or re.search('const F_M_FAULT_CONFIG_TYPE',string)):
            # remove junk charaters
            temp_var = strList[0][:strList[0].find("_FLT_CF")]
            var = temp_var.upper()
            var = var[var.find('F_M_'):]
            #  Check added to support object code variables
            tempKey = var[:7]
            if tempKey not in obj_List:
                var = (var[:5].upper()+var[5:].lower())
            supplementary,arraysize = self.findSuppFaultsandArraysize(var)
            fltmeaslist = self.createFltMeasList(var,outAppendList,supplementary,arraysize,'OUT')
            for measvar in fltmeaslist:
                self.searchA2lDictionary(measvar,outlist,"")
            fltmeaslist = self.createFltMeasList(var,charAppendList,supplementary,arraysize,'CHAR')
            for measvar in fltmeaslist:
                self.searchA2lDictionary(measvar,charlist,"")
            var_fnd =True
        elif((re.search('fault_group_read ',string)) or
        (re.search('extern',string) and re.search('F_M_FAULT_GROUP_CONFIG_TYPE',string))):
            var = strList[0][:strList[0].find("_FLT_GRP_CFG")]
            # remove junk charaters
            var = var[var.find('F_M_'):]
            grp_charlist =[]
            grp_outlist = []
            var = var.upper()
            pattern = "_GRP_FLT_APV"
            self.searchA2lDictionary(var,grp_charlist,pattern)
            # Identify the group as Fault Group or FID
            if grp_charlist:
                self.CreateFltGrpMeasList(var,obj_List, grp_charlist,grp_outlist)
            else:
                self.CreateFIDMeasList(var, obj_List, grp_charlist,grp_outlist)
            charlist.extend(grp_charlist)
            outlist.extend(grp_outlist)
            var_fnd = True
        elif((re.search('fault_group_read ',string)) or
        (re.search('extern',string) and re.search('F_M_FAULT_FID_SIG_CONFIG_TYPE',string))):
            var = strList[0]
            if strList[0].endswith("_CFG"):
                var =var[:(len(strList[0]) -4)]
            grp_charlist =[]
            grp_outlist = []
            self.CreateFIDMeasList(var, obj_List, grp_charlist,grp_outlist)
            charlist.extend(grp_charlist)
            outlist.extend(grp_outlist)
            var_fnd = True
        elif(re.search('F_M_FAULT_CONFIG_TYPE',string)       or
             re.search('F_M_FAULT_GROUP_CONFIG_TYPE',string) or
             re.search('F_M_FAULT_FID_SIG_CONFIG_TYPE',string)):
            # All types of fault variables are handled already
            var_fnd = True
        else:
            var_fnd = False
        return var_fnd

    def CreateFltGrpMeasList(self, var, obj_List, grp_charlist,grp_outlist ):
        """
            Method to identify all fault group variables associated with the
            given group name
        """
        #  Check added to support object code variables
        tempKey = var[:7]
        if tempKey not in obj_List:
            var = (var[:5].upper()+var[5:].lower())
        pattern = "(_grp_flag)|(_grp_rec)|(grp_soft)"
        self.searchA2lDictionary(var,grp_outlist,pattern)

    def CreateFIDMeasList(self, var, obj_List, grp_charlist,grp_outlist ):
        """
            Method to identify all FID variables associated with the given group
            name
        """
        pattern = "(_DFC_APV)|(_DFC_LIM_APV)|(_SIG_APV)|(_SIG_LIM_APV)"
        calibvar = var.replace("F_M","F_M_FID")
        self.searchA2lDictionary(calibvar,grp_charlist,pattern)
        #  Check added to support object code variables
        pattern = "(_fid_dfc_status)|(_fid_sig_status)|(_fid_dfc_st_flag)|(_fid_sig_st_flag)|(_fid_sat)|(_sig_sat)"
        var = var.replace("F_M_FID_SIG","F_M")
        tempKey = var[:7]
        if tempKey not in obj_List:
            var = (var[:5].upper()+var[5:].lower())
        tempKey = var[:7]
        if tempKey not in A2l.A2lDictionary.keys():
            for key_word in A2l.A2lDictionary.keys():
                if key_word.lower() == tempKey.lower():
                    var = var.replace(tempKey,key_word)
                    break
        self.searchA2lDictionary(var,grp_outlist,pattern)

    def appendCanMatrixDec(self,path,specnbr,module):
        outlist = []
        inlist = []
        ModuleDictionary[module] = (path,"",["",specnbr],[],[],[],[])
        for line in open(path):
            if(re.match("#define",line)):
                m = line.split()
                if len(m) >= 3:
                    outlist.append(m[1])
                    inlist.append(m[2])
        ModuleDictionary[module][4].extend(outlist)
        ModuleDictionary[module][5].extend(inlist)

    def searchA2lDictionary(self,var,list,matpattern,debug=False):
        key = var[:7]
        templist = []
        try:
            for msg in A2l.A2lDictionary[key]:
                Var_Fnd = False
                if (re.search(str(var),msg,re.I) and re.search(matpattern,msg,re.I)):
                    if msg not in list:
                        list.append(msg)
                    templist.append(msg)
                    Var_Fnd = True
                else:
                    if (Var_Fnd == True):
                        break;
            for tempvar in templist:
                matpattern = tempvar+"\[V\]$"
                for msg in A2l.A2lDictionary[key]:
                    if re.search(matpattern,msg):
                        if msg not in list:
                            list.append(msg)
                            break;
        except:
            pass

    @staticmethod
    def isVarInA2lDictionary(var):
        key = var[:7]
        var_fnd = False
        for msg in A2l.A2lDictionary[key]:
            if msg == var:
                var_fnd = True
                break
        return var_fnd
    def updatePriorityMeas(self):
        self.updateMeasvarMasterDictionary("c_i_maps")
        self.appendCanMatrixDec(r"src\appli\_appli\src\application_stub_pc2938_define.h","B8516195",r"application_stub_pc2938_define")


    def updateMeasvarMasterDictionary(self,module):
        chrlist = []
        inlist = []
        outlist = []
        loclist = []
        for line in open(ModuleDictionary[module][2][0]):
            #Remove the comments in the line
            if line.find(";") != -1:
                linelist = line.split(";")
#                if len(linelist)> 2:
#                    print "Module: %s line : %s " %(module,line)
                line = linelist[0]

            var = line.split()[0]
            if re.search(('_sav$|_B$|_DWork$'),var):
                pass #No need to handle this variables as it's not generated in A2l
            elif self.updateCalibration(line, chrlist,module):
                pass
            elif self.handleFaultManager(line,chrlist,inlist,outlist):
                pass
            elif self.handleCIMaps(line,chrlist):
                pass
            elif self.updateLocMeasurement(line,loclist):
                pass
            elif self.updateInMeasurement(line,inlist):
                pass
            elif self.updateOutMeasurement(line,outlist):
                pass
            else:
                if var not in self.VarNotAddedToFuncList:
                    self.VarNotAddedToFuncList.append(var)
        #Append the function list to master dictionary
        ModuleDictionary[module][3].extend(chrlist)
        ModuleDictionary[module][4].extend(outlist)
        ModuleDictionary[module][5].extend(inlist)
        ModuleDictionary[module][6].extend(loclist)

    def handleObjCodeblock(self,string,chrlist,outlist,inlist,loclist):
        charmeas = outmeas = inmeas = locmeas = False
        for line in string:
            if re.search(r"DEF_CHARACTERISTIC",line):
                if re.search(r"/begin DEF_CHARACTERISTIC",line):
                    charmeas = True
                else:
                    charmeas = False
            elif re.search(r"OUT_MEASUREMENT",line):
                if re.search(r"/begin OUT_MEASUREMENT",line):
                    outmeas = True
                else:
                    outmeas = False
            elif re.search(r"IN_MEASUREMENT",line):
                if re.search(r"/begin IN_MEASUREMENT",line):
                    inmeas = True
                else:
                    inmeas = False
            elif re.search(r"LOC_MEASUREMENT",line):
                if re.search(r"/begin LOC_MEASUREMENT",line):
                    locmeas = True
                else:
                    locmeas = False
            else:
                var = line.strip().replace(r'\n',"")
                if charmeas == True:
                    chrlist.append(var)
                    self.extractObjCodeStructName(var,chrlist)
                if  outmeas == True:
                    outlist.append(var)
                    self.extractObjCodeStructName(var,outlist)
                if inmeas == True:
                    inlist.append(var)
                    self.extractObjCodeStructName(var,inlist)
                if locmeas == True:
                    loclist.append(var)
                    self.extractObjCodeStructName(var,loclist)

    def extractObjCodeStructName(self,var,list):
        if re.search("\.",var):
            if not re.search('((_cnt)|(_APV))\.',var):
                var = var[:var.find('.')]
                if var not in list:
                    list.append(var)

    def updateObjCodeToMasterDictionary(self):
        modulename = ""
        chrlist = []
        outlist = []
        inlist = []
        loclist = []
        modulestart = False
        moduleend = False
        string = []
        for line in open(self.objfunclistmodule):
            if re.search(r"/begin FUNCTION",line):
                modulename = line.split()[2]
            elif re.search(r"FUNCTION_VERSION",line):
                version = line.split('"')[1].strip()
                modulestart = True
            elif re.search(r"/end FUNCTION",line):
                moduleend = True
            else:
                if modulestart == True and moduleend == False:
                    string.append(line)
            if modulename is not "" and modulestart == True and moduleend == True:
                self.handleObjCodeblock(string,chrlist,outlist,inlist,loclist)
                if modulename not in ModuleDictionary.keys():
                    mode = "OBJCODE"
                    ModuleDictionary[modulename]= ("",mode,["",version],chrlist,outlist,inlist,loclist)
                    # Reset all var
                    modulename = ""
                    chrlist = []
                    outlist = []
                    inlist  = []
                    loclist = []
                    string = []
                    moduleend = False
                    modulestart = False
                else:
                    print "ERROR : Object Code Module :"+modulename +" duplicate entry"
                    exit()

class Output:
    """Class to output all values"""
    def __init__(self,pcrspecdictionary,funcgroupdictionary, unrelated_table_info):
        self.excludelist = ['ESM_L2p', 'c_i_maps','F_M_Fault']
        self.pcrspecdictionary = pcrspecdictionary
        self.unrelated_table_info = unrelated_table_info
        self.funcgroupdictionary = funcgroupdictionary
        self.spec_calvar_mapping_dict = {}
        self.duplicate_cal_dict = {}

    def writeList(self,char, measlist):
        string = ""
        if measlist:
            string = self.addSpace("/begin "+char+"\n",12)
            measlist = list(set(measlist))
            measlist= sorted(measlist,key=str.lower)
            for meas in measlist:
                if MeasVar.isVarInA2lDictionary(meas):
                    string += self.addSpace(meas+"\n",16)
                else:
                    pass
            string +=self.addSpace("/end "+char+"\n",12)
        return string

    def addSpace(self,string,no_of_space = 0):
        return(string.rjust(len(string)+no_of_space))

    def removeGrpFltDuplicates(self, specnbr,grpfltdictionary):
        duptuple = [(char,ref) for char in MasterDictionary[specnbr][3]
                     for ref in grpfltdictionary.keys() if char.startswith(ref)
                     if grpfltdictionary[ref][0].upper() != specnbr.upper()]
        if duptuple:
            duplist,usedref = zip(*duptuple)
            for ref in set(usedref):
                grpfltdictionary[ref][1]= True
        else:
            duplist =[]
        filterdlist = [char for char in MasterDictionary[specnbr][3]
                            if char not in duplist]
        return filterdlist

    def removeCalVariables(self,list):
        pattern = "(_APM)|(_APT)|(_APV)|(_BPX)|(_BPY)"
        templist = list[:]
        for var in templist:
            if re.search(pattern,var):
                list.remove(var)
                #print "RemCalibVar: %s is a normal variable" %(var)
        return list

    def removeNormalVariables(self,list):
        pattern = "(_APM)|(_APT)|(_APV)|(_BPX)|(_BPY)|(DATA)"
        templist = list[:]
        for var in templist:
            if re.search("[a-z]",var) and not re.search(pattern,var):
                list.remove(var)
                #print "RemNomalVar: %s is a cal variable" %(var)
        return list

    def createModFuncList(self,spec):
        if spec not in self.excludelist:
            if (MasterDictionary[spec][3] != [] or MasterDictionary[spec][4] != [] or
                MasterDictionary[spec][5] != [] or MasterDictionary[spec][6] != [] ):
                if(re.search("[RAB]\d",spec)):
                    pcr_cur_ver = MasterDictionary[spec][0][0]
                    sw_ver = float(MasterDictionary[spec][0][2])
                    specver = max(float(MasterDictionary[spec][0][0]),
                                        float(MasterDictionary[spec][0][2]))
                    header = str(spec)
                    specver = str(specver)
                else:
                    header = spec.upper()
                    specver = ""

                string  = self.addSpace("/begin FUNCTION "+header+"\n",8)
                spectitle = MasterDictionary[spec][1].strip()
                # remove the new line character inside the string
                spectitle = " ".join(spectitle.split())
                string += self.addSpace("\""+specver+"  "+spectitle+" \" \n",12)
                string += self.addSpace("FUNCTION_VERSION \""+MasterDictionary[spec][2][0]+"\" \n",12)
                chrlist = self.removeGrpFltDuplicates(spec,Table.grpFltPriDictionary)
                chrlist = self.removeNormalVariables(chrlist)
                self.findDuplicateCalibrations(chrlist,spec)
                string += self.writeList("DEF_CHARACTERISTIC",chrlist)
                varlist = self.removeCalVariables(MasterDictionary[spec][4])
                string += self.writeList("OUT_MEASUREMENT",varlist)
                varlist = self.removeCalVariables(MasterDictionary[spec][5])
                string += self.writeList("IN_MEASUREMENT",varlist)
                varlist = self.removeCalVariables(MasterDictionary[spec][6])
                string += self.writeList("LOC_MEASUREMENT",varlist)
                string += self.addSpace("/end FUNCTION \n",8)
            else:
                string = ""
        else:
            string = ""
        return string

    def writeFunctionGroupList(self):
        fungrplist = sorted(self.funcgroupdictionary.keys(),key=str.lower)
        string = ""
        for funcgrp in fungrplist:
            string += self.addSpace("/begin FUNCTION "+funcgrp+"\n",8)
            string += self.addSpace("\""+self.funcgroupdictionary[funcgrp][1]+" \" \n",12)
            #Function Version value is stubbed
            string += self.addSpace("FUNCTION_VERSION \"0.0\" \n",12)
            string += self.addSpace("/begin SUB_FUNCTION \n",12)
            funclist = sorted(self.funcgroupdictionary[funcgrp][0],key=str.lower)
            for spec in funclist:
                string += self.addSpace(spec+"\n",16)
            string += self.addSpace("/end SUB_FUNCTION \n",12)
            string += self.addSpace("/end FUNCTION \n",8)
        return string

    def genFuncA2lFile(self):
        FILEPTR = open("A2lFunctionList.a2l",'w')
        modulelist = sorted(MasterDictionary.keys(),key=str.lower)
        string = ""
        #Generate the Group function list only if required
        if ConfigDictionary["DELPHI_GRP_FUNC_LIST_REQ"] == "TRUE":
            string += self.writeFunctionGroupList()
        for module in modulelist:
            string += self.createModFuncList(module)
            FILEPTR.write(string)
            string = ""
        FILEPTR.close()

    def mergeGeneratedFuncList(self,FILEPTR):
        FILEPTR.write("\n")
        FILEPTR.write(self.addSpace("/* ------- BEGIN A2L Function List  --------- */ \n",4))
        for line in open('A2lFunctionList.a2l'):
            FILEPTR.write(line)
        FILEPTR.write(self.addSpace("/* ------- END A2L Function List  --------- */ \n",4))
        FILEPTR.write(self.addSpace("/end MODULE\n",4))
        FILEPTR.write(self.addSpace("/end PROJECT\n"))
        print "A2L function list merged with build A2L "

    def writeObjCodeModuleBlockinA2l(self, string,module,FILEPTR):
        chrlist = []
        outlist = []
        inlist  = []
        loclist = []
        MeasVar().handleObjCodeblock(string,chrlist,outlist,inlist,loclist)
        if module not in ModuleDictionary.keys():
            mode = "OBJCODE"
            ModuleDictionary[module]= ("",mode,["",""],chrlist,outlist,inlist,loclist)
        else:
            ModuleDictionary[module][3].extend(chrlist)
            ModuleDictionary[module][4].extend(outlist)
            ModuleDictionary[module][5].extend(inlist)
            ModuleDictionary[module][6].extend(loclist)
        tempstring = ""
        chrlist = self.removeNormalVariables(ModuleDictionary[module][3])
        tempstring += self.writeList("DEF_CHARACTERISTIC",chrlist)
        varlist     = self.removeCalVariables(ModuleDictionary[module][4])
        tempstring += self.writeList("OUT_MEASUREMENT",varlist)
        varlist     = self.removeCalVariables(ModuleDictionary[module][5])
        tempstring += self.writeList("IN_MEASUREMENT",varlist)
        varlist     = self.removeCalVariables(ModuleDictionary[module][6])
        tempstring += self.writeList("LOC_MEASUREMENT",varlist)
        tempstring += self.addSpace("/end FUNCTION \n",8)
        FILEPTR.write(tempstring)
        ModuleDictionary[module][2][1] = "WRITTEN"


    def prepareFinalA2l(self,a2lname):
        a2lfuncname = re.sub(".a2l","_func.a2l",a2lname)
        FILEPTR = open(a2lfuncname,'w')
        writelineina2l = True
        string = []
        modulestart = False
        moduleend = False
        subfunc = False
        modulename = ""
        for line in open(a2lname):
            if re.search(r"/begin FUNCTION",line):
                if len(line.split()) == 3:
                    modulename = line.split()[2]
            elif re.search(r"FUNCTION_VERSION",line):
                version = line.split('"')[1].strip()
                modulestart = True
            elif re.search(r"/begin SUB_FUNCTION",line):
                subfunc = True
            elif re.search(r"/end SUB_FUNCTION",line):
                subfunc = False
            elif re.search(r"/end FUNCTION",line):
                 if modulestart == True:
                    moduleend = True
                    writelineina2l = False
            else:
                if modulestart == True and moduleend== False and subfunc == False:
                    string.append(line)
                    writelineina2l = False
            if modulename is not "" and moduleend == True and modulestart == True:
                self.writeObjCodeModuleBlockinA2l(string,modulename,FILEPTR)
                # Reset all variables
                modulename = ""
                modulestart = False
                moduleend = False
                subfunc = False
                string = []

            if re.search(r"end MODULE",line):
                self.genFuncA2lFile()
                self.mergeGeneratedFuncList(FILEPTR)
                FILEPTR.close()
                break

            if writelineina2l == True:
                FILEPTR.write(line)
            else:
                writelineina2l = True
        os.remove(a2lname);
        os.rename(a2lfuncname,a2lname);

    def generateReport(self,curpcrlabel,prepcrlabel, implementedSpecNotInPCR):
        FILEPTR = open("A2lFunctionList_info.txt",'w')
        title = "The following Specification PCR Ver number not matching with SW ver number\n"
        FILEPTR.write("".rjust(len(title),'#')+"\n")
        FILEPTR.write(title)
        FILEPTR.write("".rjust(len(title),'_')+"\n")
        for spec in MasterDictionary.keys():
            if cmp(MasterDictionary[spec][0][0],MasterDictionary[spec][0][2]) != 0 and re.search('[RAB]\d',spec):
                FILEPTR.write(spec+"\tDesc: "+MasterDictionary[spec][1]+"\tPCR Ver: "
                 +str(MasterDictionary[spec][0][0])+"\tSW Ver: "+str(MasterDictionary[spec][0][2])+"\n")
        FILEPTR.write("\n\n")
        FILEPTR.write("".rjust(len(title),'#')+"\n")
        title = "The following Specifications in PCR are not attributed to any function/module\n"
        FILEPTR.write(title)
        FILEPTR.write("".rjust(len(title),'_')+"\n")
        for spec in self.pcrspecdictionary.keys():
            if spec not in MasterDictionary.keys():
                desc = self.pcrspecdictionary[spec][1]
                import unicodedata
                desc = unicodedata.normalize('NFKD', desc).encode('ascii','ignore')
                FILEPTR.write(spec+"\tDesc: "+desc +"\tVersion: "+
                                                str(self.pcrspecdictionary[spec][0][0])+"\n")
        FILEPTR.write("\n\n")
        FILEPTR.write("".rjust(len(title),'#')+"\n")
        title = "The following Specification are changed compared to previous baseline\n"
        FILEPTR.write(title)
        FILEPTR.write("".rjust(len(title),'_')+"\n")
        for spec in MasterDictionary.keys():
            if cmp(MasterDictionary[spec][0][0],MasterDictionary[spec][0][1]) != 0:
                FILEPTR.write(spec + "\tPrevious Version: "+str(MasterDictionary[spec][0][1])+
                                        "\tCurrent Version: "+str(MasterDictionary[spec][0][0])+"\n")
        FILEPTR.write("\n\n")
        FILEPTR.write("".rjust(len(title),'#')+"\n")
        FILEPTR.close()
        FILEPTR = open("A2lFunctionList_error.txt",'w')
        FILEPTR.write("".rjust(80,'#')+"\n")
        FILEPTR.write("A2lFunctionList error report".rjust(24)+"\n")
        FILEPTR.write("".rjust(80,'#')+"\n")
        FILEPTR.write("\n\n")
        FILEPTR.write("Current customer baseline software PCR label: "+curpcrlabel+"\n")
        FILEPTR.write("Previous customer baseline software PCR label: "+prepcrlabel+"\n")
        FILEPTR.write("\n\n")
        title = "The following Modules are not attributed to any Specifications\n"
        FILEPTR.write(title)
        FILEPTR.write("".rjust(len(title),'_')+"\n")
        nuggetentrylist = ["UNUSED","HWI_CAL","GENERIC_CAL","I_C_CAL","P_T_CAL","ICC_CAL","SMC_CAL",\
        "ASM_CAL","T_D_CAL", "FDC_CAL","DTI_CAL","APP_CAL","RPC_CAL","AFC_CAL","ESM_CAL","ACM_CAL","ICI_CAL","STE_CAL","EHOOKS_CAL"]
        val_available = False
        for spec in MasterDictionary.keys():
            if not re.match('[RAB]\d',spec) and spec not in nuggetentrylist:
                for module in ModuleDictionary.keys():
                    if spec.upper() == module.upper():
                        FILEPTR.write(module + "\tModule path: "+ModuleDictionary[module][0]+"\n")
                        val_available = True
                        break
        if val_available:
            val_available = False
        else:
            FILEPTR.write("\nNULL\n")
        FILEPTR.write("\n\n")
        title = "The following Specification are implemented but not added in PCR database\n"
        FILEPTR.write(title)
        FILEPTR.write("".rjust(len(title),'_')+"\n")
        for spec in MasterDictionary.keys():
            if MasterDictionary[spec][0][3] != True and re.match('[RAB]\d',spec):
                FILEPTR.write(spec + "\tSW Version: "+str(MasterDictionary[spec][0][2])+"\n")
                val_available = True
        for spec in implementedSpecNotInPCR:
            FILEPTR.write(spec+"\t Module Name "+implementedSpecNotInPCR[spec]+".c\t\n" )
            val_available = True
        if val_available:
            val_available = False
        else:
            FILEPTR.write("\nNULL\n")
        FILEPTR.write("\n\n")
        title = "The following Information added in A2L Spec mapping table doesnt seems correct\n"
        FILEPTR.write(title)
        FILEPTR.write("".rjust(len(title),'_')+"\n")
        for line in self.unrelated_table_info:
            FILEPTR.write(line)
            val_available = True

        if val_available:
            val_available = False
        else:
            FILEPTR.write("\nNULL\n")
        FILEPTR.write("\n\n")
        title = "Unused Priority Spec List entries\n"
        FILEPTR.write(title)
        FILEPTR.write("".rjust(len(title),'_')+"\n")
        specList = sorted(Table.grpFltPriDictionary.keys(),key=str.lower)
        for spec in specList:
            if Table.grpFltPriDictionary[spec][1] != True:
                FILEPTR.write(spec+"\n")
                val_available = True
        if val_available:
            val_available = False
        else:
            FILEPTR.write("\nNULL\n")
        FILEPTR.write("\n\n")
        title = "Duplicate calibrations list \n"
        FILEPTR.write(title)
        FILEPTR.write("".rjust(len(title),'_')+"\n")
        for var in self.duplicate_cal_dict:
            FILEPTR.write(var+"  "+str([spec for spec in set(self.duplicate_cal_dict[var])])+"\n")
            val_available = True
        if val_available:
            val_available = False
        else:
            FILEPTR.write("\nNULL\n")
        FILEPTR.write("\n\n")
        FILEPTR.close()
        FILEPTR = open("A2lFunctionList_speclist.txt",'w')
        FILEPTR.write("".rjust(80,'#')+"\n")
        FILEPTR.write("A2lFunctionList speclist report".rjust(24)+"\n")
        FILEPTR.write("".rjust(80,'#')+"\n")
        FILEPTR.write("\n\n")
        for spec in MasterDictionary.keys():
            spec = spec.upper()
            if re.match('[RAB]\d',spec):
                FILEPTR.write(spec+";"+str(MasterDictionary[spec][0][0])+"\n")
        FILEPTR.write("\n\n")
        FILEPTR.close()
        FILEPTR = open("A2lFunctionList_speclist_unfound.txt",'w')
        FILEPTR.write("".rjust(80,'#')+"\n")
        FILEPTR.write("A2lFunctionList speclist unfounded report".rjust(24)+"\n")
        FILEPTR.write("".rjust(80,'#')+"\n")
        FILEPTR.write("\n\n")
        for spec in MasterDictionary.keys():
            spec = spec.upper()
            if not re.match('[RAB]\d',spec):
                FILEPTR.write(spec+";"+str(MasterDictionary[spec][0][0])+"\n")
        FILEPTR.write("\n\n")
        FILEPTR.close()

    def findDuplicateCalibrations(self,list,spec):
        for var in list:
            if var not in self.spec_calvar_mapping_dict:
                self.spec_calvar_mapping_dict[var] = spec
            elif spec != self.spec_calvar_mapping_dict[var]:
                if var not in self.duplicate_cal_dict:
                    self.duplicate_cal_dict[var] = [self.spec_calvar_mapping_dict[var],spec]
                else:
                    self.duplicate_cal_dict[var].append(spec)
            else:
                pass

    def cleanDiskMemory(self):
        print "Removing temp files and directories..please wait.."
        if exists('A2lFunctionList.a2l'):
            os.remove('A2lFunctionList.a2l')
        if exists(r"..\..\gill_vob\6_coding\Ctags"):
            shutil.rmtree(r"..\..\gill_vob\6_coding\Ctags")

#Constant for Indicator of Change
C_SPEC = 0
C_VER = 1
C_IOC = 2
C_BL  = 3

class IndicatorOfChange:
    """ Class to Identify the Indicator of Change """
    def __init__(self,cur_baseline,pcrlabel,pcrspecdictionary, nuggetsModuleDictionary = {},legacyIocDict= {}):
        self.cur_baseline = cur_baseline
        self.pcrlabel = pcrlabel
        self.nuggetsModuleDictionary = nuggetsModuleDictionary
        self.pcrspecdictionary = pcrspecdictionary
        self.change_detected = False
        self.ref_indicator = dict()
        self.legacyIocDict = legacyIocDict
        self.unusedLegacyEntries = []
        self.implementedSpecNotInPcr = dict()
        self.function_grp_dictionary = dict()
        self.ref_indicator = self.getReferenceIndicator(REF_INDICATOR_FILEPATH)
        self.createMasterDictionary()
        self.createFunctionGroupDictionary()
        self.indicator_of_change =self.calculateIndicatorOfChange()
        self.updateIndicatorOfChange(REF_INDICATOR_FILEPATH)

    def getReferenceIndicator(self,FILEPATH):
        ref_indicator = {}
        for line in open(FILEPATH):
            line = line.strip()
            if not re.match("#",line):
                ref_indicator[line.split("\t")[C_SPEC].split(":")[1]] = (
                                            line.split("\t")[C_SPEC].split(":")[1],
                                            line.split("\t")[C_VER].split(":")[1],
                                            line.split("\t")[C_IOC].split(":")[1],
                                            line.split("\t")[C_BL].split(":")[1])
            else:
                if line.find("Baseline") != -1:
                    print "Reference Indicator Baseline: %s" %(line.replace("#","").strip().split(":")[1])
        return ref_indicator

    def setReferenceIndicator(self,FILEPATH):
        FILEPTR = open(FILEPATH,'w')
        string = "############# Tool Generated: Please don't modify it manually ###########\n"
        string +="#############         Baseline:"+self.cur_baseline+"               ###########\n"
        string +="#########################################################################\n"
        FILEPTR.writelines(string)
        speclist = sorted(self.indicator_of_change.keys(),key=str.lower)
        for spec in speclist:
            if str(self.indicator_of_change[spec][C_VER]) != "0.0":
                FILEPTR.write("SpecNumber:"+spec+"\tVersion:"+str(self.indicator_of_change[spec][C_VER])+
                                "\tIOC:"+str(self.indicator_of_change[spec][C_IOC])+
                                "\tBaseline:"+str(self.indicator_of_change[spec][C_BL])+"\n")
        FILEPTR.close()

    def accessCleartool(self,cmd):
        try:
            p = subprocess.Popen(cmd,shell = False,stdin = subprocess.PIPE,
                               stdout = subprocess.PIPE,stderr = subprocess.STDOUT)
            version = p.stdout.read()
            print version
        except:
            print "Exception detected in cleartool operation"

    def updateIndicatorOfChange(self,FILEPATH):
        if len(self.ref_indicator.keys()) != len(self.indicator_of_change.keys()):
            self.change_detected = True
        else:
            for spec in self.indicator_of_change.keys():
                if spec not in self.ref_indicator.keys():
                    self.change_detected = True

        if self.change_detected == True:
            print "Specification change detected"
        else:
            print "No specification change detected "
        # Is current baseline delivery version
        try:
            if ConfigDictionary["UPDATE_REF_IND_CHANGE"] !="FALSE" and self.change_detected == True:
                cmd = 'cleartool checkout -nc ' +FILEPATH
                self.accessCleartool(cmd)
                self.setReferenceIndicator(FILEPATH)
        except:
            print "Unable to checkout the Indicator of Change Module"
#            comment = "Indicator updated for "+str(self.cur_baseline)
#            cmd = 'cleartool checkin -c "' +comment+'" '+modulename
#            self.accessCleartool(cmd)


    def calculateIndicatorOfChange(self):
        indicator_of_change = dict()
        for spec in MasterDictionary.keys():
            if re.match('[RAB]\d',spec):
                if cmp(MasterDictionary[spec][0][0],MasterDictionary[spec][0][1]) != 0:
                    if spec in self.ref_indicator.keys():
                        if self.ref_indicator[spec][C_VER] != MasterDictionary[spec][0][0]:
                            baseline = self.cur_baseline
                            pre_indicator = self.ref_indicator[spec][C_IOC]

                            if spec not in self.legacyIocDict.keys():
                                new_indicator = (str(int(pre_indicator.split(".")[0])+1)+"."+
                                                pre_indicator.split(".")[1])
                                spec_version = MasterDictionary[spec][0][0]
                            else:
                                if float(self.legacyIocDict[spec][0]) >= MasterDictionary[spec][0][0]:
                                    if self.legacyIocDict[spec][1] == 'LOWER_DIGIT':
                                        new_indicator = (pre_indicator.split(".")[0]+"."+
                                                        str(int(pre_indicator.split(".")[1])+1))
                                        spec_version = self.legacyIocDict[spec][1]
                                    else:
                                        new_indicator = (str(int(pre_indicator.split(".")[0])+1)+"."+
                                                        pre_indicator.split(".")[1])
                                        spec_version = MasterDictionary[spec][0][0]
                                else:
                                    # Normal method appiled. The entry in the table could be wrong
                                    new_indicator = (str(int(pre_indicator.split(".")[0])+1)+"."+
                                                    pre_indicator.split(".")[1])
                                    spec_version = MasterDictionary[spec][0][0]
                                    # Error Reported to update the table
                                    line = spec+";"+self.legacyIocDict[spec][0]+";"+self.legacyIocDict[spec][1]+";"+"IndicatorOfChange"
                                    self.unusedLegacyEntries.append(line)
                        else:
                            baseline = self.ref_indicator[spec][C_BL]
                            new_indicator = self.ref_indicator[spec][C_IOC]
                            spec_version = self.ref_indicator[spec][C_VER]
                    else:
                        new_indicator = "0.0"
                        spec_version = MasterDictionary[spec][0][0]
                        baseline = self.cur_baseline
                else:
                    if spec in self.ref_indicator.keys():
                        if spec not in self.legacyIocDict.keys():
                            new_indicator = self.ref_indicator[spec][C_IOC]
                            spec_version = self.ref_indicator[spec][C_VER]
                        else:
                            pre_indicator = self.ref_indicator[spec][C_IOC]
                            if float(self.legacyIocDict[spec][0]) >= MasterDictionary[spec][0][0]:
                                if self.legacyIocDict[spec][1] == 'LOWER_DIGIT':
                                    new_indicator = (pre_indicator.split(".")[0]+"."+str(int(pre_indicator.split(".")[1])+1))
                                    spec_version = self.legacyIocDict[spec][1]
                                else:
                                    new_indicator = (str(int(pre_indicator.split(".")[0])+1)+"."+pre_indicator.split(".")[1])
                                    spec_version = MasterDictionary[spec][0][0]
                            else:
                                # Normal method appiled. The entry in the table could be wrong
                                new_indicator = (str(int(pre_indicator.split(".")[0])+1)+"."+ \
                                                pre_indicator.split(".")[1])
                                spec_version = MasterDictionary[spec][0][0]
                                # Error Reported to update the table
                                line = spec+";"+self.legacyIocDict[spec][0]+";"+self.legacyIocDict[spec][1]+";"+"IndicatorOfChange"
                                self.unusedLegacyEntries.append(line)
                        baseline = self.ref_indicator[spec][C_BL]

                    else:
                        new_indicator = "0.0"
                        baseline = self.cur_baseline
                        spec_version = MasterDictionary[spec][0][0]
                indicator_of_change[spec] = (spec,spec_version,new_indicator,baseline)
                #Update the MasterDictionary with the correct IOC
                MasterDictionary[spec][2][0] = indicator_of_change[spec][C_IOC]
        return indicator_of_change

    def createFunctionGroupDictionary(self):
        """ OPL272: Specs to be classified based on the Function groups """
        for spec in MasterDictionary.keys():
            #No need to update the group if the spec contains no variables
            if (MasterDictionary[spec][3] != [] or MasterDictionary[spec][4] != [] or
               MasterDictionary[spec][5] != [] or MasterDictionary[spec][6] != [] ):
                if re.match("[RAB]\d",spec):
                    func_grp = self.pcrspecdictionary[spec][2]
                    import unicodedata
                    func_grp = unicodedata.normalize('NFKD', func_grp).encode('ascii','ignore')
                    if func_grp not in self.function_grp_dictionary.keys():
                        desc = self.pcrspecdictionary[spec][3]
                        desc = unicodedata.normalize('NFKD', desc).encode('ascii','ignore')
                        self.function_grp_dictionary[func_grp] = ([spec],desc)
                    else:
                        self.function_grp_dictionary[func_grp][0].append(spec)
                else:
                    func_grp = "GENERIC"
                    if func_grp not in self.function_grp_dictionary.keys():
                        self.function_grp_dictionary[func_grp] = ([spec],"Generic functions ")
                    else:
                        self.function_grp_dictionary[func_grp][0].append(spec)

    def createMasterDictionary(self):
        """
        Inputs :
            1. Spec number,version, and Measurements from ModuleDictionary from SW
            2. Spec version for current and previous baseline and spec description
            from PCR database
            3. Indicator of Change info from Spec_Indicatorofchange_mapping.txt
        Output:
            MasterDictionary which contains all above inputs.
        Desc :
            Master Dictionary which contains info about versions, measurements and
            indicator of change is created from various inputs.
        """
        for module in ModuleDictionary.keys():
            # Don't consider object code variables
            if ModuleDictionary[module][1] != "OBJCODE":
                #Find the spec numbers
                spec = ModuleDictionary[module][2][1]
                spec = spec.upper()
                if re.match('[RAB]\d',spec):
                    if spec.find("_") != -1:
                        specnbr = spec[:spec.find('_')]
                        specver = spec[spec.find('_')+1:]
                        if specver.find(";") != -1:
                            specver = specver[:specver.find(";")]
                        if specver.find("_") != -1:
                            specver = specver[:specver.find('_')]
                    else:
                        specnbr = spec
                        specver = 0.0
                else:
                    specnbr = spec
                    specver = 0.0
                # Calculate Indicator of Change
                indicatorofchange = ['0.0']
                # Convert the string
                try:
                    specver = float(specver)
                except:
                    print "Specver %s is not correct" %(specver)

                #Is check number valid ?
                if re.match('[RAB]\d',specnbr):
                    # Is spec defined in PCR database
                    if specnbr in self.pcrspecdictionary.keys():
                        pcrspecavail = True
                        cur_bl_pcr_spec_ver = self.pcrspecdictionary[specnbr][0][0]
                        if cur_bl_pcr_spec_ver == "":
                            cur_bl_pcr_spec_ver = 0.0
                            self.implementedSpecNotInPcr[specnbr]= module
                        pre_bl_pcr_spec_ver = self.pcrspecdictionary[specnbr][0][1]
                        pcr_spec_desc = self.pcrspecdictionary[specnbr][1]
                    else:
                        self.implementedSpecNotInPcr[specnbr]= module
                        pcrspecavail = False
                        cur_bl_pcr_spec_ver = 0.0
                        pre_bl_pcr_spec_ver = 0.0
                        specnbr = "TO_BE_DETERMINED"
                        pcr_spec_desc = specnbr
                else:
                    pcrspecavail = False
                    cur_bl_pcr_spec_ver = 0.0
                    pre_bl_pcr_spec_ver = 0.0
                    if module not in self.nuggetsModuleDictionary.keys():
                        pcr_spec_desc = module
                        specnbr = module
                    else:
                        specnbr = self.nuggetsModuleDictionary[module]
                        pcr_spec_desc = self.nuggetsModuleDictionary[module]

                if re.search("_$",specnbr):
                    specnbr = specnbr[:-1]

                #Make all spernbr as uppercase letter
                specnbr = specnbr.upper()

                if specnbr not in MasterDictionary.keys():
                    MasterDictionary[specnbr] =([cur_bl_pcr_spec_ver,pre_bl_pcr_spec_ver,
                                                 specver, pcrspecavail],
                                                 pcr_spec_desc,indicatorofchange,
                                                 ModuleDictionary[module][3],
                                                 ModuleDictionary[module][4],
                                                 ModuleDictionary[module][5],
                                                 ModuleDictionary[module][6])
                else:
                    if specver > MasterDictionary[specnbr][0][2]:
                        MasterDictionary[specnbr][0][2] = specver
                    if ModuleDictionary[module][3] != []:
                        MasterDictionary[specnbr][3].extend(ModuleDictionary[module][3])
                    if ModuleDictionary[module][4] != []:
                        MasterDictionary[specnbr][4].extend(ModuleDictionary[module][4])
                    if ModuleDictionary[module][5] != []:
                        MasterDictionary[specnbr][5].extend(ModuleDictionary[module][5])
                    if ModuleDictionary[module][6] != []:
                        MasterDictionary[specnbr][6].extend(ModuleDictionary[module][6])




class Table:
    """Class to handle miscellenous requirements """
    spectable = 'A2l_spec_mapping_table.txt'
    grpFltPriDictionary = {}

    def __init__(self):
        self.unrelated_table_info = []
        self.nuggetsModuleDictionary = {}
        self.legacyIocDict = {}

    def readConfigurationInfo(self):
        for line in open(self.spectable):
            lineList = line.strip().split(";")
            if (not re.match(r'#',line)) and (len(lineList)== 4) and lineList[2] == 'config':
                ConfigDictionary[lineList[0]] = lineList[1]

    def readLegacyIoc(self):
        for line in open(self.spectable):
            lineList = line.strip().split(";")
            if (not re.match(r'#',line)) and (len(lineList)== 5) and lineList[3] == 'IndicatorOfChange':
                self.legacyIocDict[lineList[0]] = (lineList[1],lineList[2])

    def updateFaultCodeInfofromTable(self):
        chrlist = inlist = outlist = []
        for line in open(self.spectable):
            lineList = line.strip().split(";")
            if (not re.match(r'#',line)) and (len(lineList)== 6) and lineList[4] == 'fault':
                string = lineList[0]+" fault_set  ;"
                MeasVar().handleFaultManager(string,chrlist,inlist,outlist)
                if (chrlist == [] and inlist == [] and outlist == []):
                    self.unrelated_table_info.append(line)
                else:
                    if lineList[1] in ModuleDictionary.keys():
                        ModuleDictionary[lineList[1]][3].extend(chrlist)
                        ModuleDictionary[lineList[1]][4].extend(outlist)
                        ModuleDictionary[lineList[1]][5].extend(inlist)
                    else:
                        spec = (lineList[2]+"_"+lineList[3])
                        ModuleDictionary[lineList[1]] = ("","",["",spec],chrlist,outlist,inlist,[])
                    chrlist = []
                    inlist = []
                    outlist = []


    def updateVariablefromTable(self):
        for line in open(self.spectable):
            lineList = line.strip().split(";")
            if not re.match('#',line)  and len(lineList)== 6 and lineList[4]!= 'fault':
                var = lineList[0]
                templist = []
                if lineList[4] == 'Characteristic':
                    matpattern = str(var.upper())+"($)|(_\d)"
                else:
                    matpattern = str(var)+"($)|(_\d)"
                MeasVar().searchA2lDictionary(var,templist,matpattern)
                if templist != []:
                    if lineList[4] == 'Characteristic':
                        if lineList[1] in ModuleDictionary.keys():
                            ModuleDictionary[lineList[1]][3].extend(templist)
                        else:
                            ModuleDictionary[lineList[1]] = ("","",["",(lineList[2]+"_"+lineList[3])],templist,[],[],[])
                    if lineList[4] == 'Output':
                        if lineList[1] in ModuleDictionary.keys():
                            ModuleDictionary[lineList[1]][4].extend(templist)
                        else:
                            ModuleDictionary[lineList[1]] = ("","",["",(lineList[2]+"_"+lineList[3])],[],templist,[],[])
                    if lineList[4] == 'Input':
                        if lineList[1] in ModuleDictionary.keys():
                                ModuleDictionary[lineList[1]][5].extend(templist)
                        else:
                            ModuleDictionary[lineList[1]] = ("","",["",(lineList[2]+"_"+lineList[3])],[],[],templist,[])
                    if lineList[4] == 'Local':
                        if lineList[1] in ModuleDictionary.keys():
                            ModuleDictionary[lineList[1]][6].extend(templist)
                        else:
                            ModuleDictionary[lineList[1]] = ("","",["",(lineList[2]+"_"+lineList[3])],[],[],[],templist)


                else:
                    self.unrelated_table_info.append(line)

    def getSpecNbrfromTable(self,module):
        spec_nbr_fnd = False
        for line in open(self.spectable):
            lineList = line.strip().split(";")
            if not re.match('#',line) and len(lineList)== 6 and module == lineList[1]:
                if lineList[1] in ModuleDictionary.keys():
                    ModuleDictionary[module][2][1] = line.split(";")[2].upper()+"_"+line.split(";")[3]
                else:
                    ModuleDictionary[lineList[1]] = ("","",["",(lineList[2].upper()+"_"+lineList[3])],[],[],[],[])
                spec_nbr_fnd = True
                break
        return spec_nbr_fnd

    def attributeSpecNbrfromTable(self,pcrspecdictionary = {}):
        for line in open(self.spectable):
            lineList = line.strip().split(";")
            if not re.match('#',line) and 4 == len(lineList) and 'module' == lineList[2]:
                if lineList[0] in ModuleDictionary.keys():
                    specnbr = lineList[1].upper()
                    if not re.search("[RAB]\d",specnbr):
                        spec = specnbr + "0.0"
                        if lineList[0] not in self.nuggetsModuleDictionary.keys():
                            self.nuggetsModuleDictionary[lineList[0]] = (specnbr)
                        else:
                            self.unrelated_table_info.append(line+ " Entry already added\n")
                    elif specnbr in pcrspecdictionary.keys():
                        if pcrspecdictionary[specnbr][0][0] != "":
                            spec = specnbr+"_"+str(pcrspecdictionary[specnbr][0][0])
                        else:
                            spec = specnbr+"_"+'0.0'
                            self.unrelated_table_info.append(line)
                    else:
                        spec = specnbr+"_"+'0.0'
                        self.unrelated_table_info.append(line)
                    ModuleDictionary[lineList[0]][2][1] = spec
                else:
                    self.unrelated_table_info.append(line)

    def prepareGrpFltPriDictionary(self):
        for line in open(self.spectable):
            if re.search("Priority_Spec_List",line):
                lineList = line.strip().split(";")
                Table.grpFltPriDictionary[lineList[0]] = [lineList[1],False]

    def updateTabletoMasterDictionary(self,pcrspecdictionary = {}):
        self.updateFaultCodeInfofromTable()
        self.updateVariablefromTable()
        self.readLegacyIoc()
        self.attributeSpecNbrfromTable(pcrspecdictionary)
        for line in open(self.spectable):
            lineList = line.split(";")
            if not re.match('#',line) and len(lineList)>= 5:
                self.getSpecNbrfromTable(lineList[1])
        self.prepareGrpFltPriDictionary()

def main():
    print "####################################################"
    try:
        print "Start Time : %s" %(time.ctime(time.time()))
        import sys
        a2lfilename =  sys.argv[1]
        if not exists(a2lfilename):
            sys.exit("A2L file %s not exist" %(a2lfilename))
        else:
            print "Generating A2L Function list for %s" %(a2lfilename)
        #Update the Configuration
        insTable = Table()
        insTable.readConfigurationInfo()
        if (ConfigDictionary["PROJECT_NAME"] == "DCM2.7"):
            Customer_Interface_Available = True
            Object_Code_Available = True
        else:
            Customer_Interface_Available = False
            Object_Code_Available = False
        custinfo = ConfigDictionary["PROJ_PCR_CODE"]
        threads = []
        thread = threading.Thread(target=partial(A2l,a2lfilename))
        threads.append(thread)
        print "Generating ctags modules"
        insCtags = Ctags()
        thread =threading.Thread(target=insCtags.genCtagsOutput)
        threads.append(thread)
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        print "Get PCR Information"
        insPcr = Pcr(custinfo)
        insPcr.extractPcrData()
        print "Current Baseline :%s used PCR label:%s " %(insPcr.swlabel,insPcr.curpcrlabel)
        print "Previous Baseline:%s used PCR Label:%s " %(insPcr.preswlabel,insPcr.prepcrlabel)

        #Instanciating Measvar and updating C_I_Maps list
        insMeasVar = MeasVar()
        insMeasVar.updatePriorityMeas()
        insSpec = Spec()
        ##############################################################
        #  Part 2: Extract implementation data and process each module
        ##############################################################
        threadid = threading.Thread(target=partial(
                        insSpec.updateSpecnbrMasterDictionary,insPcr.pcrspecdictionary))
        threadid.start()
        for module in ModuleDictionary.keys():
            if exists(ModuleDictionary[module][2][0]):
                thread = threading.Thread(target=partial(
                                insMeasVar.updateMeasvarMasterDictionary,module))
                thread.start()
                threads.append(thread)
                if (threading.activeCount() > 4):
                    for t in threads:
                        t.join()
                    threads = []
        insMeasVar.updateObjCodeToMasterDictionary()
        print "updating mapping table information  "
        threadid.join()
         ##############################################################
        #  Part 3: Extract implementation data and process each module
        ##############################################################
        insTable.updateTabletoMasterDictionary(insPcr.pcrspecdictionary)
        insIOC = IndicatorOfChange(insPcr.swlabel,insPcr.curpcrlabel,insPcr.pcrspecdictionary,
                            insTable.nuggetsModuleDictionary, insTable.legacyIocDict)
        insTable.unrelated_table_info.extend(insIOC.unusedLegacyEntries)
        insOutput = Output(insPcr.pcrspecdictionary,insIOC.function_grp_dictionary,
                            insTable.unrelated_table_info)
        insOutput.prepareFinalA2l(a2lfilename)
        insOutput.generateReport(insPcr.curpcrlabel,
                                    insPcr.prepcrlabel,
                                    insIOC.implementedSpecNotInPcr)
        insOutput.cleanDiskMemory()
        print "End Time : %s" %(time.ctime(time.time()))
        print "DCM2.7 A2l Function List generated successfully "
    except:
        print "Exception occured. Please fix it"
        traceback.print_exc(file=sys.stdout)
        sys.exit()

    print "####################################################"


if __name__ == '__main__':
    main()
