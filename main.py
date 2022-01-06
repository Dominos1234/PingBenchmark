import time

import matplotlib.pyplot as plt
import matplotlib
from matplotlib.animation import FuncAnimation
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

matplotlib.use("TkAgg")

import subprocess, platform, os
import tkinter as tk
from tkinter import ttk

anims=[]
x_vals = []
y_vals = []
numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
count = 0
start = 0

MY_FONT = ("Verdana", 14)

f = Figure(figsize=(5, 5), dpi=100)
a = f.add_subplot(111)


def ping(host):
    param = '-n'
    command = ['ping', param, '1', host]
    res = str(subprocess.check_output(command))

    print(res)
    id = res.find("Average =")
    time = res[id + 10:id + 13]

    if time[0] in numbers and time[1] in numbers and time[2] in numbers:
        time = int(time)
    elif time[0] in numbers and time[1] in numbers:
        time = int(time[0:2])
    else:
        time = int(time[0])
    return time

    return res


host = 'github.com'


def animate(i):
    global count, ani, start
    if count < timer:
        y = ping(host)
        count = count + 1
        x_vals.append(count)
        y_vals.append(y)

        a.clear()
        a.plot(x_vals, y_vals, 'o')
    else:
        start = 0
        ani.event_source.stop()

def Start():
    global host,timer,start,ani,count,f,x_vals,y_vals

    if(start==0):
        start = 1
        a.clear()
        x_vals=[]
        y_vals=[]
        count = 0

        host = iphostEntry.get()
        timer = int(timerEntry.get())
        ani = FuncAnimation(f, animate, interval=1000)
        #anims.append(ani)

        canvas = FigureCanvasTkAgg(f)
        canvas.draw()
        canvas.get_tk_widget().grid(row=0, column=4, rowspan=5)
        canvas._tkcanvas.grid(row=0, column=4, rowspan=5)



def Add():
    t = int(timerEntry.get())
    timerEntry.delete(0, tk.END)
    timerEntry.insert(0, t + 1)


def Subtract():
    t = int(timerEntry.get())
    timerEntry.delete(0, tk.END)
    timerEntry.insert(0, t - 1)


app = tk.Tk()

iphostEntry = tk.Entry(app, width=40, borderwidth=5)
iphostEntry.grid(row=1, column=0)
iphostEntry.insert(0, "google.com")

label2 = tk.Label(app, text="Nazwa hosta / Adres IP", width=40)
label2.grid(row=0, column=0)

start_button = tk.Button(app, text="Start", command=Start, width=60)
start_button.grid(row=2, column=0, columnspan=4)

label3 = tk.Label(app, text="Średni czas odpowiedzi: ", width=50)
label3.grid(row=5, column=4)

label1 = tk.Label(app, text="Czas trwania pomiaru (s)", width=20)
label1.grid(row=0, column=1, columnspan=3)

label5 = tk.Label(app, text="Historia poprzednich pomiarów", width=50)
label5.grid(row=3, column=0, columnspan=2)

history = tk.Frame(app, width=100,height=300)
history.grid(row=4, column=0, columnspan=2)

timerEntry = tk.Entry(app, width=10, borderwidth=5)
timerEntry.grid(row=1, column=1)
timerEntry.insert(0, "10")

plus_button = tk.Button(app, text="+", command=Add, width=1)
plus_button.grid(row=1, column=2)

minus_button = tk.Button(app, text="-", command=Subtract, width=1)
minus_button.grid(row=1, column=3)

canvas = FigureCanvasTkAgg(f)
canvas.draw()
canvas.get_tk_widget().grid(row=0, column=4, rowspan=5)
canvas._tkcanvas.grid(row=0, column=4, rowspan=5)

# toolbar = NavigationToolbar2Tk(canvas, app)
# toolbar.update()

def update():
    if len(y_vals)!=0:
        average = round(sum(y_vals) / len(y_vals),2)
        label3['text']="Średni czas odpowiedzi: "+str(average)+"ms"
        app.after(1000, update)
    else:
        label3['text'] = "Średni czas odpowiedzi: 0ms"
        app.after(1000, update)

app.after(1000, update)

app.mainloop()
