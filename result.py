import pandas as pd
from fpdf import FPDF
from matplotlib import pyplot as plt

def createpdf(point_csv):
    # model.modelcon()
    result_data=pd.read_csv(point_csv, index_col=0)
    length = len(result_data)/5
    pdf = FPDF()
    pdf.set_auto_page_break(auto=False)
    pdf.add_page(orientation='L')
    pdf.set_x(0)
    pdf.set_y(0)
    pdf.set_margins(0, 0)
    pdf.set_left_margin(0)
    pdf.set_font('Arial', 'B', size=20)
    pdf.set_fill_color(170)
    pdf.rect(0,0, 80, 250, 'F')
    pdf.image('Report_logo.png', 10, 10, 60, 60, "PNG")

    pdf.set_x(100)
    pdf.set_y(0)
    pdf.set_left_margin(90)
    # pdf.set_font('Arial', 'B', size=15)
    pdf.cell(30, 30, txt="1. model and CV Graph", ln=4, align='L')
    plt.plot(result_data)
    plt.ylim([0, 120])

    plt.yticks([20, 40, 60, 80, 100])
    plt.xticks([length, length*2, length*3, length*4])
    plt.legend(['cv', 'ml'])
    plt.savefig('data/cv_and_ml.png')
    pdf.image('data/cv_and_ml.png', 80, 20, 180, 90, "PNG",'data/cv_and_ml.png')

    plt.cla()

    pdf.set_font('Arial', 'B', size=20)
    pdf.cell(30, 170, txt="2. Result Graph", ln=4, align='L')
    result_data['ml+cv']=result_data['cv']*0.3+result_data['ml']*0.7
    plt.plot(result_data['ml+cv'])
    plt.ylim([0, 120])
    plt.yticks([20, 40, 60, 80, 100])
    plt.xticks([length, length*2, length*3, length*4])

    plt.savefig('data/cv+ml.png')
    pdf.image('data/cv+ml.png', 80, 120, 180, 90, "PNG", 'data/cv+ml.png')
    pdf.output("ResultReport1.pdf", 'F')
createpdf('data/point/point_csv.csv')