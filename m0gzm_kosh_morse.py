#! /usr/bin/env python
'''
Cosole bases kosh morse practice script

'''

from __future__ import print_function
import argparse
import sys
import os
import time
import random
import argparse
import re
import subprocess
import operator
import pygame

# globals
tone        = 0
wpm         = 20
timer       = 0
dot         = 1
dash        = dot * 3
char_space  = 1 
word_space  = char_space * 3
verbose     = False
min_chars   = 2
max_chars   = 26
ONE_UNIT    = 0.5
THREE_UNITS = 3 * ONE_UNIT
SEVEN_UNITS = 7 * ONE_UNIT
PATH        = 'morse_sound_files/'

 
CODE = {'A': '.-',     'B': '-...',   'C': '-.-.',
        'D': '-..',    'E': '.',      'F': '..-.',
        'G': '--.',    'H': '....',   'I': '..',
        'J': '.---',   'K': '-.-',    'L': '.-..',
        'M': '--',     'N': '-.',     'O': '---',
        'P': '.--.',   'Q': '--.-',   'R': '.-.',
        'S': '...',    'T': '-',      'U': '..-',
        'V': '...-',   'W': '.--',    'X': '-..-',
        'Y': '-.--',   'Z': '--..',
         
        '0': '-----',  '1': '.----',  '2': '..---',
        '3': '...--',  '4': '....-',  '5': '.....',
        '6': '-....',  '7': '--...',  '8': '---..',
        '9': '----.'
        }
         
k_letters = ['K', 'M', 'R', 'S', 'U', 'A', 'P', 'T', 'L', 'O', 'W', 'I', '.', 'N', 'J', 'E', 'F', '0', 'Y', ',', 'V', 'G', '5', '/', 'Q', '9', 'Z', 'H', '3', '8', 'B', '?', '4', '2', '7', 'C', '1', 'D', '6', 'X']
 
def main():
     
    msg = raw_input('MESSAGE: ')
    verify(msg)
     
    pygame.init()
     
    for char in msg:
        if char == ' ':
            print(' '*7,)
            time.sleep(SEVEN_UNITS)
        else:
            print(CODE[char.upper()],)
            pygame.mixer.music.load(PATH + char.upper() + '_morse_code.ogg')
            pygame.mixer.music.play()
            time.sleep(THREE_UNITS)


def verify(string):
    keys = CODE.keys()
    for char in string:
        if char.upper() not in keys and char != ' ':
            sys.exit('Error the charcter ' + char + ' cannot be translated to Morse Code')
 




def main() :
    parser = argparse.ArgumentParser(
    description = __doc__,
    epilog= ''
    )
    parser.add_argument('-s', help='character speed', action='store',      dest='speed')
    parser.add_argument('-t', help='tone',            action='store',      dest='tone')
    parser.add_argument('-v', help='verbose mode',    action='store_true', dest='verbose')
    args = parser.parse_args()

    if args.speed:
        # Use specified character speed
        character_speed = args.speed
    else:
        character_speed = 20

    if args.tone:
        # Use specified character tone 
        character_tone = args.tone
    else:
        character_tone = 60

    if args.verbose:
        verbose = True









if __name__ == "__main__":
    main()


