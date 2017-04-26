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





# connect to db
cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER=FRBLO-DB04;DATABASE=DB_SAM;UID=BloisElectronic;PWD=Blois1@#$%')
cur = cnxn.cursor()





connectionstring = """
SELECT 
  [schema] = s.name,
  [table]  = t.name, 
  [column] = c.name
FROM 
  sys.tables AS t
INNER JOIN
  sys.schemas AS s
  ON t.[schema_id] = s.[schema_id]
INNER JOIN 
  sys.columns AS c
  ON t.[object_id] = c.[object_id]
ORDER BY 
  t.name, 
  c.name;
"""
cur.execute(connectionstring)
#cur.execute(connectionstring_b, label )
print 'ALL'
while True:
    row = cur.fetchone()
    if row == None:
        break
    print row[0], row[1], row[2] 



connectionstring = "SELECT * FROM [dbo].[TB_CUSTOMERS]"           
cur.execute(connectionstring)
print "\n\n\nTB_CUSTOMERS"
while True:
    row = cur.fetchone()
    if row == None:
        break
    print row[0], row[1], row[2], row[3], row[4], row[5] 
print '\n\n\n'


connectionstring = "SELECT * FROM [dbo].[TB_PACKAGES]"
cur.execute(connectionstring)
for _ in range(50):
    row = cur.fetchone()
    if row == None:
        break
    print (row[0], row[1], row[2], row[3], row[4], row[5], row[6], 
           row[7], row[8], row[9], row[10], row[11], row[12], row[13],
           row[14], row[15], row[16], row[17], row[18])
print '\n\n\n'


print '\n\n\nSUBSET of 500'
for _ in range(500):
    row = cur.fetchone()
    if row == None:
        break
    print row[7], row[6], row[15], row[17], row[18]
print '\n\n\n'






connectionstring = """SELECT SPV_REFERENCE_FK,SPV_VERSION,SPV_TITLE,SPC_SHORT_LABEL,SPC_LABEL
            FROM TB_PACKAGES
            INNER JOIN TB_PACKAGE_SPECIFICATIONS ON PSP_PACK_FK=PCK__PK
            AND PCK_HARDWARE_FK+PCK_CUSTOMER_FK+PCK_SOFTWARE_FK+PCK_VARIANT+PCK_VERSION= ?
            INNER JOIN TB_SPECIFICATION_VERSIONS ON SPV__PK=PSP_SPEC_FK AND PCK_Type=1
            INNER JOIN TB_SPECIFICATION_REFERENCES ON SPR__PK = SPV_REFERENCE_FK
            INNER JOIN TB_SPECIFICATION_CATEGORIES ON SPC__PK = SPR_CATEGORY_FK
            ORDER BY SPC_SHORT_LABEL,SPV_REFERENCE_FK"""

label = "1EWCHAPP_A100D010"
cur.execute(connectionstring, label )
print 'LABLE'
for _ in range(50):
    row = cur.fetchone()
    if row == None:
        break
    print row[7], row[6], row[15], row[17], row[18]
print '\n\n\n'



cnxn.close()

