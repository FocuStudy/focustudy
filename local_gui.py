import collections
import cv2
import pandas as pd

from gaze_tracking.gaze_tracking import GazeTracking
import tkinter as tk
from PIL import ImageTk, Image  # Pillow
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import datetime
import numpy as np
import time
import os
import result

scoredata = pd.read_csv('point_csv.csv', index_col='time')
cv_list=list(scoredata['cv'])
ml_list=list(scoredata['ml'])
plot_list_cv=[]
plot_list_ml=[]
frame_cnt=0
timelist=[]
model_pointer = 2

cap = cv2.VideoCapture('student_video.mp4')
cap.set(3, 840)
cap.set(4, 680)
fps = int(cap.get(cv2.CAP_PROP_FPS))

win = tk.Tk()

win.title("Focustudy")
win.iconphoto(False, tk.PhotoImage(file='../focustudy/logo.png'))
win.geometry("800x640+50+50")
win.resizable(True, True)
win.configure(background='white')

frm = tk.Frame(win, bg="white", width=300, height=300)
frm.grid(row=0, column=1)

mfrm = tk.Frame(win, bg="white", width=500, height=300)
mfrm.grid(row=0, column=0)

perfrm = tk.Frame(win, bg="white", width=500, height=300)
perfrm.grid(row=1, column=0)

Listfrm = tk.Frame(win, bg="white", width=300, height=300)
Listfrm.grid(row=1, column=1)

button = tk.Button(win, overrelief="solid", command=lambda: exit_gui(), text='종료', width=15, repeatdelay=100)
button.grid(row=2, column=1)
lbl1 = tk.Label(frm)
lbl1.grid(row=0, column=0)

li = tk.Listbox(Listfrm, selectmode='extended', font=("Times", 13), height=15, width=30)
li.place(x=0, y=0)

fig = Figure(figsize=(5, 3), dpi=100)
fig2 = Figure(figsize=(5, 3), dpi=100)

def exit_gui():
    result.createpdf('point_csv.csv')
    exit()



def video():
    global frame_cnt, timelist, model_pointer, timer
    global plot_list_cv, plot_list_ml
    ret, frame = cap.read()

    frame_cnt += 1
    print(frame_cnt)

    if not ret:
        exit_gui()

    frame = cv2.flip(frame, 1)
    fig2.clear()
    if frame_cnt == fps * 5:
        timer=timer + datetime.timedelta(seconds=5)
        timelist.append(str(timer))
        frame_cnt = 0
        plot_list_cv.append(cv_list[0])
        plot_list_ml.append(ml_list[0])
        del cv_list[0]
        del ml_list[0]
        LineGraph = fig2.add_subplot(1, 1, 1)
        # result_list.append(scorelist[-1]*0.3 + model_list[model_pointer-2]*0.7)
        result_list = np.array(plot_list_cv) * 0.3 + np.array(plot_list_ml) * 0.7
        # print(scorelist[-1] , model_list[model_pointer-2])
        LineGraph.plot(timelist[-10:], result_list[-10:])
        LineGraph.set_title('Graph')
        LineGraph.set_xticklabels(timelist[-10:], fontsize=6, rotation=25, ha='right')
        LineGraph.set_ylim([0, 120])
        LineGraph.set_yticks([20, 40, 60, 80, 100])

        if len(timelist) >= 2:
            canvas = FigureCanvasTkAgg(fig2, master=perfrm)
            canvas.get_tk_widget().grid(column=0, row=0)

        fig.clear()

        if len(timelist) >= 2:
            LineGraph = fig.add_subplot(1, 1, 1)
            LineGraph.plot(timelist[-10:], plot_list_cv[-10:])
            LineGraph.plot(timelist[-10:], plot_list_ml[0: model_pointer][-10:])
            # print(timelist[-10:], model_list[0: model_pointer][-10:])
            model_pointer += 1
            LineGraph.set_title('model and CV Graph')
            LineGraph.set_xticklabels(timelist[-10:], fontsize=6, rotation=25, ha='right')
            LineGraph.set_ylim([0, 120])
            LineGraph.set_yticks([20, 40, 60, 80, 100])
            canvas = FigureCanvasTkAgg(fig, master=mfrm)
            canvas.get_tk_widget().grid(column=0, row=0)


    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    frame = cv2.resize(frame, (200, 200), interpolation=cv2.INTER_CUBIC)

    img = Image.fromarray(frame)
    imgtk = ImageTk.PhotoImage(image=img)

    lbl1.imgtk = imgtk
    lbl1.configure(image=imgtk)
    lbl1.after(20, video)


timer = datetime.timedelta(seconds=0)
video()
win.mainloop()