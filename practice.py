
# import modules
import os
import pygame

# pygame specific locals/constants
from pygame.locals import *

# some resource related warnings
if not pygame.font: print('Warning, fonts disabled')
if not pygame.mixer: print('Warning, sound disabled')


# replacing loops
# ===============
#for e in lst: 
#    func(e) # statement-based loop


#map(func,lst) # map()-based loop




# Map-based action sequence
# =========================
# let's create an execution utility function
do_it = lambda f: f()

# let f1, f2, f3 (etc) be functions that perform actions
def f1():
    print 'this is f1'

def f2():
    print 'this is f2'

def f3():
    print 'this is f3'





map(do_it, [f1,f2,f3]) # map()-based action sequence



pr = lambda s:s
namenum = lambda x: (x==1 and pr("one")) \
                 or (x==2 and pr("two")) \
                 or (pr("other"))

print namenum(2)


