

#import pyPdf
import time
import datetime as dt
import calendar
import re
import StringIO
from reportlab.lib import colors
from reportlab.lib import utils
from reportlab.lib.pagesizes import landscape, A4
from reportlab.platypus import (Image, SimpleDocTemplate, Paragraph, Spacer)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch, mm
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, inch, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
 

# constants
CALENDER_FILE     = "calendar_form.pdf"
YEAR              = 2017
FIRST_DAY_OF_WEEK = calendar.MONDAY # for calendar class.
START_DAY         = 0 #Calendar starting day, default of 0 means Mondau, 2 for Tuesday, etc
OUT_FILE          = 'Calender.tex'
MONTHS            = ['January', 'Febuary', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'Decemebr']
BIRTHDAY_FILE     = 'birthdays.xml'
ANIVERSARY_FILE   = 'aniverseries.xml'
DATES_FILE        = 'dates.xml'



def main():
    ''' the main function '''
    # invoke calendar data instant
    first_day_of_week = START_DAY # Monday
    data = calendar_data()

    # invoke month class
    jan = calendar_grid(YEAR, 'January', data, first_day_of_week) 
    #jan.draw()

    jan.make_month()
    
class calendar_grid:
    '''
    Class:          calendar_grid
    Description:    represents a month
    Requirements:   None
    '''
    def __init__(self, year, month, data, first_day_of_week=0):
        '''
        Method:         __init__
        Parameters:     year as integer
                        month as string
                        first_day_of_week, zero = Monday
                        data class instant
        Returns:        None
        Description:    Initialise all variables.
                        Invokes the Table instant
        '''
        # local variables
        self._first_day_of_week = first_day_of_week
        self._data = data
        self._year = year
        self._month = month
        self._elements = []
        self._doc = SimpleDocTemplate(CALENDER_FILE, pagesize=landscape(A4))
        # invoke calender class calc
        self.cal = calendar
        self.cal.setfirstweekday(FIRST_DAY_OF_WEEK)
    def _make_title(self):
        '''
        Method:         _make_title
        Parameters:     None
        Returns:        None
        Description:    Sets up the month name followed by the year year.
        '''
        self._title=Table([[self._month + ' ' + str(self._year)]])
        self._title.setStyle(TableStyle([('ALIGN' ,(0,0),(0,0), 'CENTRE'),
                                         ('VALIGN',(0,0),(0,0), 'BOTTOM'),]))
    def _make_day_headers(self, first_day=0):
        '''
        Method:         _make_day_headers
        Parameters:     Calendar week start day, defaults to Monday.
        Returns:        None
        Description:    Sets up the first row of the month table with the day names
                        depending on the first day of the week.
        '''
        day_set = ['Monday', 'Tuesday', 'Wedensday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        # set up days depending on first day o fthe week, zero being monday.
        days_in_week = 7
        day_pointer  = first_day
        days = [[day_set[(day_pointer + day_of_week) % days_in_week] for day_of_week in range(days_in_week)]]
        # set up the day header table
        self._week = Table(days,7*[1.2*inch], 1*[0.25*inch])
        self._week.setStyle(TableStyle([('ALIGN' ,(0,0),(-1,-1), 'CENTRE'),
                                        ('VALIGN',(0,0),(-1,-1), 'MIDDLE'),
                                        ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                                        ('BOX', (0,0), (-1,-1), 0.25, colors.black),
                                       ]))
    def _make_data(self):
        '''
        Method:         _make_data
        Parameters:     None
        Returns:        None
        Description:    produce data for each day of the month, if it exists.
        '''

        # For first week add blank days before 1st of month

    
        data= [['Mon', '01', '02', '03', '04', '03', '04'],
               ['10', '11', '12', '13', '14', '03\nB:John (44)\nA:M&M', '04'],
               ['20', '21', '22', '23', '24', '03', '04'],
               ['20', '21', '22', '23', '24', '03', '04'],
               ['30', '31', '32', '33', '34', '03', '04']]

        self._week_data=Table(data,7*[1.2*inch], 5*[1.1*inch])
        self._week_data.setStyle(TableStyle([('ALIGN' ,(0,0),(-1,-1),'RIGHT'),
                                             ('VALIGN',(0,0),(-1,-1),'TOP'),
                                             ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                                             ('BOX', (0,0), (-1,-1), 0.25, colors.black),
                                            ]))
    def _blank_days(self):
        '''
        Method:         _blank_days
        Parameters:     None
        Returns:        number of blank days
        Description:    Calculate blank days at beginning of month table.
        '''
        blanks = self.first_day + 1
        #print 'first day = ' + DAYS[self.first_day] + '  blanks = ' + str(blanks)
        if blanks >= 7:
            return blanks - 7
        else:
            return blanks
    def make_month(self):
        '''
        Method:         make_month
        Parameters:     None
        Returns:        None
        Description:    Produces the completed grid for the month.
        '''
        self._make_title()
        self._make_day_headers(self._first_day_of_week)
        self._make_data()
        self._elements.append(self._title)
        self._elements.append(self._week)
        self._elements.append(self._week_data)
        self._doc.build(self._elements)

class calendar_data:
    '''
    Class:          calendar_data
    Description:    Represents calendar data containerh
    Requirements:   None
    '''
    '''  '''
    def __init__(self):
        '''
        Method:         __init__
        Parameters:     None
        Returns:        None
        Description:    Initialise all variables.
        '''
        self._birthdays = []
        self._aniversaries = []
        self._appointments = []
        self._build_birthdays()
        self._build_aniversaries()
        self._build_appointment()
    def _build_birthdays(self):
        '''
        Method:         _build_birthdays
        Parameters:     None
        Returns:        None
        Description:    builds the birthdays for a year.
        '''
        self._birthdays.append({'month':'4' , 'day':'14', 'name':'Mark'  , 'year':1985})
        self._birthdays.append({'month':'4' , 'day':'28', 'name':'Sue'   , 'year':1956})
        self._birthdays.append({'month':'4' , 'day':'28', 'name':'Mia'   , 'year':2010})
        self._birthdays.append({'month':'8' , 'day':'12', 'name':'John'  , 'year':1954})
        self._birthdays.append({'month':'8' , 'day':'20', 'name':'Janet' , 'year':1958})
        self._birthdays.append({'month':'8' , 'day':'20', 'name':'Dave'  , 'year':1958})
        self._birthdays.append({'month':'9' , 'day':'26', 'name':'Mum'   , 'year':1926})
        self._birthdays.append({'month':'10', 'day':'29', 'name':'Lin'   , 'year':1947})
        self._birthdays.append({'month':'12', 'day':'11', 'name':'Freya' , 'year':2013})
        self._birthdays.append({'month':'12', 'day':'14', 'name':'James' , 'year':1987})
    def _build_aniversaries(self):
        '''
        Method:         _build_aniversaries
        Parameters:     None
        Returns:        None
        Description:    builds the aniversaries for a year.
        '''
        #self._aniversaries.append({'month':'7' , 'day':'27', 'name':'Mark & Mirel'   , 'year':2014})
        #self._aniversaries.append({'month':'8' , 'day':'18', 'name':'Janet & Dave' , 'year':1987})
        self._aniversaries.append({'month':'8' , 'day':'18', 'name':'Janet' , 'year':1987})
        #self._aniversaries.append({'month':'9' , 'day':'26', 'name':'Dean & Same'    , 'year':2015})
    def _build_appointment(self):
        '''
        Method:         _build_appointment
        Parameters:     None
        Returns:        None
        Description:    builds the appointments for a year.
        '''
        self._appointments.append({'month':'9' , 'day':'2' , 'name':'Audax Ugley'})
        self._appointments.append({'month':'9' , 'day':'6' , 'name':'Lin Spain'})
        self._appointments.append({'month':'9' , 'day':'15', 'name':'Lin Home'})
        self._appointments.append({'month':'9' , 'day':'30', 'name':'Honda Insurance'})
        self._appointments.append({'month':'10', 'day':'7' , 'name':'Audax GtDunmow'})
        self._appointments.append({'month':'10', 'day':'9' , 'name':'John dentist 17:30'})
        self._appointments.append({'month':'11', 'day':'3' , 'name':'Hong Kong'})
        self._appointments.append({'month':'12', 'day':'1' , 'name':'Home'})
    def get(self, month, day):
        '''
        Method:         get
        Parameters:     Month and day
        Returns:        The compiled data.
        Description:    Compiles birthdays, anivarsaries and appointments for a given day.
        '''
        results = []
        # birthdays:
        month_list = filter(lambda month_list: str(month) == month_list['month'], self._birthdays)
        day_list =   filter(lambda day_list: str(day) == day_list['day'], month_list)
        for people in day_list:
            pass #results.append('B:' + people['name'] + ' (' +  str(CALENDER_YEAR - people['year']) + ')')
        # aniversaries:
        month_list = filter(lambda month_list: str(month) == month_list['month'], self._aniversaries)
        day_list =   filter(lambda day_list: str(day) == day_list['day'], month_list)
        for people in day_list:
            results.append('A:' + people['name'] + ' (' +  str(CALENDER_YEAR - people['year']) + ')')
        # appointments
        month_list = filter(lambda month_list: str(month) == month_list['month'], self._appointments)
        day_list =   filter(lambda day_list: str(day) == day_list['day'], month_list)
        for people in day_list:
            pass #results.append(people['name'])
        return results

if __name__ == '__main__':
    main()
    print "PDF created!"

