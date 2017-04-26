#! /usr/bin/env python
'''
Script to run the peg word system test.

Version: peg_system    0.3    15-04-2015

'''

import sys
import os
import time
import random
import argparse


# globals

peg_words_list = [
'tie',   'noah',  'ma',    'ray',   'law',   'shoe',  'key',   'ivy',   'bee',  'toes',
'toad',  'tin',   'dam',   'mark',  'doll',  'dish',  'dog',   'dove',  'tap',  'nose',
'Net',   'Nun',   'Gnome', 'Nero',  'Nail',  'Notch', 'Neck',  'Knife', 'Knob', 'Mouse',
'Mat',   'Moon',  'Mummy', 'Mower', 'Mole',  'Match', 'Mug',   'Movie', 'Map',  'Rose',
'Rat',   'Rain',  'Ram',   'Roar',  'Reel',  'Rash',  'Rock',  'Roof',  'Rope', 'Lace',
'Lad',   'Lane',  'Lamb',  'Lair',  'Lolly', 'Leech', 'Leg',   'Loaf',  'Lip',  'Cheese',
'Sheet', 'Chain', 'Jam',   'Jar',   'Jail',  'Judge', 'Shack', 'Chef',  'Ship', 'Goose',
'Cat',   'Coin',  'Comb',  'Car',   'Coal',  'Cage',  'Cake',  'Cave',  'Cab',  'Vase',
'Fat',   'Phone', 'Foam',  'Fire',  'File',  'Fish',  'Fog',   'Fife',  'Fob',  'Bus',
'Bat',   'Bone',  'Bomb',  'Bar',   'Ball',  'Beach', 'Pig',   'Puff',  'Pipe', 'Daisies']


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



    if start_num < 99 and 0 == test_size:
        test_size = ask_for_test_size(start_num)
    import_peg_words(start_num, test_size, peg_dict)
    run_test(start_num, test_size, peg_dict)



def ask_for_test_size(start_num):
    ''' request user to input test size '''
    print('How many peg words to test?')
    print('any number between 1 and %d' %(max_peg_words - start_num))
    return check_size(start_num, int(raw_input('Input:')))



def check_size(start_num, size):
    ''' keep size within limits '''
    limit = max_peg_words - start_num
    if size > limit:
        print('size limited to %d' % limit)
        size = limit
    elif size < 1:
        print('size limited to 1')
        size = 1 
    return size



def import_peg_words(start_num, size, dict):
    ''' load sub set of words into test dictionary '''
    for index in range(start_num - 1, size):
        dict[str(index + 1)] = peg_words_list[index]



def run_test(start_num, size, dict):
    # shuffle the peg word dictionary
    items = dict.items()
    random.shuffle(items)
    print 'Identify these ' , size , ' Peg Words\n'
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
        map(pprint, correct_answers)
    else:
        print('\nAll Correct')



def dump_peg_words(start_num, num):
    ''' get words '''
    count = start_num - 1
    for __ in range(num):
        line = peg_words_list[count]
        count = count + 1
        print str(count) + ' ' + line



def get_peg_word(num):
    ''' read a particular word '''
    print 'Peg Word %d is %s' %(num, peg_words_list[num - 1])



def pprint(words):
    ''' helper makes print a function for use in map '''
    print words


if __name__ == '__main__':
    main()

