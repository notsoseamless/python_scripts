from os.path import join
import re
import os
import sys
sys.path = [ join(sys.prefix, 'Lib', 'site-packages', 'scons-0.96.1'), join(sys.prefix, 'Lib', 'site-packages', 'scons'), join(sys.prefix, 'scons-0.96.1'), join(sys.prefix, 'scons')] + sys.path
currentpath = os.getcwd()
currentpath = re.sub(r'[\\\/]gill_vob[\\\/]\d_coding',r'\\tcg_misc_tool_vob\\tools\\python\\site-packages',currentpath)
sys.path.append(currentpath)
import SCons.Script
SCons.Script.main()