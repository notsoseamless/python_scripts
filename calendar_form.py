
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


# constants
CALENDER_FILE = "calendar_form.pdf"
YEAR = 2017


def main():

    #from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
     
    canvas = canvas.Canvas(CALENDER_FILE, pagesize=A4)
     
   # canvas.drawString(30,750,'OFFICIAL COMMUNIQUE')
   # canvas.drawString(30,735,'OF ACME INDUSTRIES')
   # canvas.drawString(500,750,"12/12/2010")
   # canvas.line(480,747,580,747)
     
    #canvas.drawString(275,725,'AMOUNT OWED:')
    #canvas.drawString(500,725,"$1,000.00")
    #canvas.line(378,723,580,723)
    # 
    #canvas.drawString(30,703,'RECEIVED BY:')
    #canvas.line(120,700,580,700)
    #canvas.drawString(120,703,"JOHN DOE")

    # invoke month class
    jan = month(canvas, YEAR, 'January') 
    jan.draw()
    
    canvas.showPage()
    canvas.save()



class month:
    ''' represents a month '''
    def __init__(self, c, year, month):
        ''' init method '''
        # local variables
        self.c = c
        self.year = year
        self.month = month

    def draw(self):
        ''' draws a month '''
        self.c.setFont('Helvetica', 12)
        self.c.setLineWidth(.3)
        self.c.drawString(30,750,self.month + '  ' + str(self.year))

















if __name__ == "__main__":
    main()


