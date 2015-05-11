#! /usr/bin/env python
'''

Script to run the peg word system test.

Todo:
fix the arg parser
replace importing of peg words with array

'''

import sys
import os
import time
import random
import argparse


# globals
version = 'peg_system    0.3    15-04-2015'
verbose = False

peg_words_list=[\
'tie',\
'noah',\
'ma',\
'ray',\
'law',\
'shoe',\
'tap',\
'ivy',\
'bee',\
'toes',\
'toad',\
'tin',\
'dam',\
'tyre',\
'doll',\
'dish',\
'dog',\
'dove',\
'tap',\
'nose',\
'Net',\
'Nun',\
'Gnome',\
'Nero',\
'Nail',\
'Notch',\
'Neck',\
'Knife',\
'Knob',\
'Mouse',\
'Mat',\
'Moon',\
'Mummy',\
'Mower',\
'Mole',\
'Match',\
'Mug',\
'Movie',\
'Map',\
'Rose',\
'Rat',\
'Rain',\
'Ram',\
'Roar',\
'Reel',\
'Rash',\
'Rock',\
'Roof',\
'Rope',\
'Lace',\
'Lad',\
'Lane',\
'Lamb',\
'Lair',\
'Lolly',\
'Leech',\
'Leg',\
'Loaf',\
'Lip',\
'Cheese',\
'Sheet',\
'Chain',\
'Jam',\
'Jar',\
'Jail',\
'Judge',\
'Shack',\
'Chef',\
'Ship',\
'Goose',\
'Cat',\
'Coin',\
'Comb',\
'Car',\
'Coal',\
'Cage',\
'Cake',\
'Cave',\
'Cab',\
'Vase',\
'Fat',\
'Phone',\
'Foam',\
'Fire',\
'File',\
'Fish',\
'Fog',\
'Fife',\
'Fob',\
'Bus',\
'Bat',\
'Bone',\
'Bomb',\
'Bar',\
'Ball',\
'Beach',\
'Pig',\
'Puff',\
'Pipe',\
'Daisies']

max_peg_words = len(peg_words_list)


def main():
    start_num = 1
    test_size = 0
    peg_dict  = {}

    parser = argparse.ArgumentParser(
    description = __doc__,
    epilog= ''
    )
    parser.add_argument('-s', '--sta', help=': STArting NUMber of peg words to test', type=int)
    parser.add_argument('-n', '--num', help=': NUMber of peg words to test', type=int)
    parser.add_argument('-d', '--dum', help=': DUMp a list of DUMP peg words to stdio', type=int)
    parser.add_argument('-g', '--get', help=': Get peg word GET', type=int)
    parser.add_argument('-V', '--version', help=': Print the version', action='store_true', dest='display_version')
    parser.add_argument('-v', '--verbose', help=': Verbose mode', action='store_true', dest='verbose')
    args = parser.parse_args()

    if args.sta:
        # start number of peg words to test
        start_num = int(args.sta)
        if start_num > max_peg_words or start_num < 1:
            print('Only between 1 and ' + str(max_peg_words))
            exit(1)

    if args.num:
        # number of peg words to test
        test_size = check_size(start_num, int(args.num))

    if args.dum:
        # dump the peg words
        num = check_size(start_num, int(args.dum))
        dump_peg_words(start_num, num)
        exit(2)

    if args.get:
        # read out a particular word
        choice = args.get
        if choice > max_peg_words or choice < 1:
            print('Only between 1 and ' + str(max_peg_words))
        else:
            print(peg_words_list[int(choice) - 1])
        exit(2)

    if args.verbose: vebose = True

    if args.display_version:
        print('Version: ' + version)
        exit(2)

    if start_num < 99 and 0 == test_size:
        test_size = ask_for_test_size(start_num)
    if verbose: print('Started')
    import_peg_words(start_num, test_size, peg_dict)
    run_test(start_num, test_size, peg_dict)
    if verbose: print('Finished')



def ask_for_test_size(start_num):
    print('How many peg words to test?')
    print('any number between 1 and %d' %(max_peg_words - start_num))
    return check_size(start_num, int(raw_input('Input:')))



def check_size(start_num, size):
    ''' keep size in limits '''
    limit = max_peg_words - start_num
    if limit < size:
        print('size limited to %d' % limit)
        return limit
    elif(size < 1):
        return 1 
    else:
        return size



def import_peg_words(start_num, size, dict):
    # load words into dictionary
    index = start_num
    for i in range(size):
        index = str(i + 1)
        name =peg_words_list[i] 
        dict[index] = name



def run_test(start_num, size, dict):
    if verbose: print('run test')
    # shuffle the peg word dictionary
    items = dict.items()
    random.shuffle(items)
    dict = items
    # use dictionary to ask questions
    print 'Identify these ' , size , ' Peg Words'
    print
    correct_num = 0
    correct_answers = []
    for index, name in items:
        answer = raw_input(index + ': ')
        if name.strip().lower() == answer.lower():
            print('Correct')
            correct_num = correct_num + 1
        else:
            print('Wrong ' + index + ' is ' + name)
            correct_answers.append(index + '  ' + name)
    if correct_num < size:
        print('\nYou got ' + str(correct_num) + ' out of ' + str(size))
        print('Here is what you got wrong:')
        for ans in correct_answers:
            print ans,
    else:
        print('\nAll Correct')



def dump_peg_words(start_num, num):
    # get words
    count = start_num - 1
    for i in range(num):
        line = peg_words_list[count]
        count = count + 1
        print str(count) + ' ' + line



def get_peg_word(num):
    # read a particular word
    word = peg_words_list[num-1]
    print 'Peg Word %d is %s' %(num, word)


if __name__ == '__main__':
    main()

