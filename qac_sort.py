'''
script sorts qac survey
runs in 6_coding/qac 
'''
import os
import glob
import re

def main():
    
    regex_match = re.compile('.html$')
    filelist = os.listdir('out')
    for filename in filelist:
        if regex_match.search(filename):
            print filename








if __name__ == '__main__':
    main()



