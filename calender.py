'''
   
   calender generator

   Script to generate a year calendar
   Will import aniversaries etc from an external text file

   Author: John Oldman - May 2017

'''

import time
import datetime as dt
import calendar
import matplotlib.pyplot as plt
import numpy as np
import xml.etree.ElementTree as ET
import re




#constants
CALENDER_YEAR     = 2017
FIRST_DAY_OF_WEEK = calendar.SUNDAY # beware because Calendar and latex sty are different.
START_DAY         = 1 #Calendar starting day, default of 1 means Sunday, 2 for Monday, etc
OUT_FILE          = 'Calender.tex'
MONTHS            = ['', 'January', 'Febuary', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'Decemebr']
DAYS              = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'] 
BIRTHDAY_FILE     = 'birthdays.xml'
ANIVERSARY_FILE   = 'aniverseries.xml'
DATES_FILE        = 'dates.xml'





def main():
    ''' main function '''

    # time this module
    start = time.clock()

    # create and run the year object
    year = Year(2017, START_DAY)
    year.draw()
    year.output()

    # calculate module run time 
    print 'Run time was ' + str(time.clock() - start) + ' seconds.'




def write_to_file(src_list):
    ''' generate the output file from the src list '''
    file_ptr = ''
    try:
        file_ptr = open(OUT_FILE, 'w')
    except IOError:
        print 'failed to open ' + OUT_FILE 
        sys.exit()
    for line in src_list:
        file_ptr.write(line )
    file_ptr.close()


def append_to_file(src_list):
    ''' generate the output file from the src list '''
    file_ptr = ''
    try:
        file_ptr = open(OUT_FILE, 'a')
    except IOError:
        print 'failed to open ' + OUT_FILE 
        sys.exit()
    for line in src_list:
        file_ptr.write(line )
    file_ptr.close()


class Year:
    ''' represents a year object '''

    def __init__(self, year, StartingDayNumber):
        ''' init function '''
        self.year = year
        self.StartingDayNumber = StartingDayNumber
        self.header_buffer = []
        self.footer_buffer = []
        # initialise month objects
        self.month_obs = []
        for month in range(1, 13):
            self.month_obs.append(Month(year, month))

    def draw(self):
        self.create_header()
        for month in self.month_obs:
            month.draw()
        self.create_footer()

    def create_header(self):
        ''' create header '''
        self.header_buffer.append('\\documentclass[landscape,a4paper]{article}')
        self.header_buffer.append('\\usepackage{calendar} % Use the calendar.sty style')
        self.header_buffer.append('\\usepackage[landscape,margin=0.5in]{geometry}')
        self.header_buffer.append('\\begin{document}')
        self.header_buffer.append('\\pagestyle{empty} % Removes the page number from the bottom of the page')
        self.header_buffer.append('\\noindent')
        self.header_buffer.append('\\StartingDayNumber=' + str(self.StartingDayNumber))
        self.header_buffer.append('')

    def create_footer(self):
        ''' create footer '''
        self.footer_buffer.append('')
        self.footer_buffer.append('\\end{document}')

    def output(self):
        ''' create output '''
        write_to_file('')
        for line in self.header_buffer:
            append_to_file(line + '\n')
        for month in self.month_obs:
            month.output()
        for line in self.footer_buffer:
            append_to_file(line + '\n')




class Month:
    ''' represents a month object '''

    def __init__(self, year, month):
        ''' init function '''
        # invoke occurances class
        self.occ = occurances()
        # invoke calender class c
        self.c = calendar
        self.c.setfirstweekday(FIRST_DAY_OF_WEEK)
        # local variables
        self.year = year
        self.month = month
        self.page_buffer = []
        self.first_day, self.num_days = self.c.monthrange(self.year, self.month)

    def draw(self):
        ''' generates month data '''
        self.page_buffer.append('')
        self.page_buffer.append('%----------------------------------------------------------------------------------------')
        self.page_buffer.append('%	MONTH AND YEAR SECTION')
        self.page_buffer.append('%----------------------------------------------------------------------------------------')
        self.page_buffer.append('')
        self.page_buffer.append('\\begin{center}')
        self.page_buffer.append('\\textsc{\LARGE ' + MONTHS[self.month] + '} ')
        self.page_buffer.append('\\textsc{\LARGE ' + str(self.year) + '} ')
        self.page_buffer.append('\\end{center}')
        self.page_buffer.append('')
        self.page_buffer.append('%----------------------------------------------------------------------------------------')
        self.page_buffer.append('')
        self.page_buffer.append('\\begin{calendar}{\hsize}')
        self.page_buffer.append('')
        self.page_buffer.append('%----------------------------------------------------------------------------------------')
        self.page_buffer.append('%	BLANK DAYS BEFORE THE BEGINNING OF THE CALENDAR')
        self.page_buffer.append('%----------------------------------------------------------------------------------------')
        self.page_buffer.append('')
        for day in range(self.blank_days()):
            self.page_buffer.append('\\BlankDay')
        self.page_buffer.append('')
        self.page_buffer.append('%----------------------------------------------------------------------------------------')
        self.page_buffer.append('%	NUMBERED DAYS AND CALENDAR CONTENT')
        self.page_buffer.append('%----------------------------------------------------------------------------------------')
        self.page_buffer.append('')
        self.page_buffer.append('\\setcounter{calendardate}{1} % Start the date counter at 1')
        self.page_buffer.append('')
        space = self.get_spacing()
        # offset by one as days start at 1
        for day in range(1, self.num_days + 1):
            insert_info = str(self.occ.get(self.month, day))[2:-2]
            print insert_info
            self.page_buffer.append('\\day{}{\\vspace{' + space + '}' + str(insert_info) + '} % ' + str(day))
        self.page_buffer.append('')    
        self.page_buffer.append('% Un-comment the \BlankDay below if the bottom line of the calendar is missing')
        self.page_buffer.append('\\BlankDay')
        self.page_buffer.append('')
        self.page_buffer.append('%----------------------------------------------------------------------------------------')
        self.page_buffer.append('\\finishCalendar')
        self.page_buffer.append('\\end{calendar}')
        self.page_buffer.append('\\newpage')

    def blank_days(self):
        ''' calculate blank days at beginning of month table '''
        blanks = self.first_day + 1
        #print 'first day = ' + DAYS[self.first_day] + '  blanks = ' + str(blanks) 
        if blanks >= 7:
            return blanks - 7
        else:
            return blanks
        
    def output(self):
        ''' outputs month data '''
        for line in self.page_buffer:
            append_to_file(line + '\n')

    def get_spacing(self):
        ''' determine what spacing we need '''      

        #print str(self.year) + '  '  +  str( self.month)  +  '  ' + str((self.c.month(self.year, self.month)).count('\n') - 2)

        # this is a bodge to keep formatting in line - need to fix later.
        if 6 == (self.c.month(self.year, self.month).count('\n') - 2):
            return '2.0cm'
        else:
            return '2.5cm'



class occurances:
    ''' represents regular occurances object '''
    def __init__(self):
        ''' init method '''
        self.birthdays = []
        self.aniversaries = []
        self.appointments = []
        self.build_birthdays()
        self.build_aniversaries()
        self.build_appointment()

    def build_birthdays(self):
        ''' builds birthdays '''
        self.birthdays.append({'month':'1' , 'day':'1' , 'name':'Nobody', 'year':1985})
        self.birthdays.append({'month':'4' , 'day':'14', 'name':'Mark'  , 'year':1985})
        self.birthdays.append({'month':'4' , 'day':'28', 'name':'Sue'   , 'year':1956})
        self.birthdays.append({'month':'4' , 'day':'28', 'name':'Mia'   , 'year':2010})
        self.birthdays.append({'month':'8' , 'day':'12', 'name':'John'  , 'year':1954})
        self.birthdays.append({'month':'9' , 'day':'26', 'name':'Mum'   , 'year':1926})
        self.birthdays.append({'month':'10', 'day':'29', 'name':'Lin'   , 'year':1947})
        self.birthdays.append({'month':'12', 'day':'11', 'name':'Freya' , 'year':2013})
        self.birthdays.append({'month':'12', 'day':'14', 'name':'James' , 'year':1987})
            
    def build_aniversaries(self):
        ''' builds aniversaries '''
        self.aniversaries.append({'month':'4', 'day':'28', 'name':'Test Anniv' , 'year':1981})
        self.aniversaries.append({'month':'4', 'day':'28', 'name':'Test2 Anniv' , 'year':0})
        self.aniversaries.append({'month':'8', 'day':'18', 'name':'Janet and Dave' , 'year':1987})

    def build_appointment(self):
        ''' build appointments '''
        self.appointments.append({'month':'9', 'day':'9', 'name':'John dentist 17:30'})
        self.appointments.append({'month':'4', 'day':'28', 'name':'test'})

    def get(self, month, day):
        ''' returns occurances for day in a month '''
        results = []
        #month_list = []
        #day_list = []

        # birthdays:
        month_list =  filter(lambda month_list: str(month) == month_list['month'],  self.birthdays)
        day_list =    filter(lambda day_list:   str(day)   == day_list['day'],      month_list)
        for people in day_list:
            results.append('B:' + people['name'] + ' (' +  str(CALENDER_YEAR - people['year']) + ')')

        # aniversaries:
        month_list =  filter(lambda month_list: str(month) == month_list['month'],  self.aniversaries)
        day_list =    filter(lambda day_list: str(day) ==  day_list['day'],  month_list)
        for people in day_list:
            results.append('A:' + people['name'] + ' (' +  str(CALENDER_YEAR - people['year']) + ')')

        # appointments
        month_list =  filter(lambda month_list: str(month) == month_list['month'],  self.appointments)
        day_list =    filter(lambda day_list: str(day) ==  day_list['day'],  month_list)
        for people in day_list:
            results.append(people['name'])

        
        return results

    


if __name__ == "__main__":
    main()


