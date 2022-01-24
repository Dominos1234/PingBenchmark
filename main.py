import datetime
import time
import sqlite3
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.animation import FuncAnimation
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

matplotlib.use("TkAgg")

import subprocess, platform, os
import tkinter as tk
from tkinter import ttk

anims = []
x_vals = []
y_vals = []
numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
count = 0
start = 0
current_select = "x: [x]"

MY_FONT = ("Verdana", 14)

f = Figure(figsize=(5, 5), dpi=100)
a = f.add_subplot(111)

con = sqlite3.connect('test.db')
cur = con.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS tests (id INTEGER PRIMARY KEY, ip TEXT, date TEXT)''')
cur.execute('''CREATE TABLE IF NOT EXISTS pings (test_id INTEGER, count INTEGER, time REAL, FOREIGN KEY(test_id) 
                REFERENCES tests(id))''')


def insert_test_to_db(ip):
    today_time = datetime.datetime.now().strftime("%H:%M:%S %d-%m-%y")
    cur.execute('''INSERT INTO tests (ip, date) VALUES (?, ?)''', [ip, today_time])
    return cur.lastrowid


def insert_ping_to_db(test_id, ping_count, ping_time):
    cur.execute('''INSERT INTO pings (test_id, count, time) VALUES (?, ?, ?)''', [test_id, ping_count, ping_time])
    return


def remove_test_from_db(id):
    cur.execute('''DELETE FROM tests WHERE id = ?''', [id])
    return


def remove_selected_from_db():
    split_str = current_select.split("    -    ")
    cur.execute('''DELETE FROM tests WHERE date = ? AND ip = ?''', [split_str[0], split_str[1]])
    populate_history(listBox)
    return


def populate_history(listBox):
    listBox.delete(0, tk.END)
    cur.execute('''SELECT ip, date FROM tests''')
    rows = cur.fetchall()
    for row in rows:
        listBox.insert(0, row[1] + "    -    " + row[0])
    return


def show_plot():
    global x_vals, y_vals
    split_str = split_str = current_select.split("    -    ")
    cur.execute('''SELECT id FROM tests WHERE date = ? AND ip = ?''', [split_str[0], split_str[1]])
    cur_id = cur.fetchone()[0]
    cur.execute('''SELECT count, time FROM pings WHERE test_id = ?''', [cur_id])
    rows = cur.fetchall()
    x_vals = []
    y_vals = []
    for row in rows:
        x_vals.append(row[0])
        y_vals.append(row[1])
    a.clear()
    a.plot(x_vals, y_vals, '-o')
    canvas = FigureCanvasTkAgg(f)
    canvas.draw()
    canvas.get_tk_widget().grid(row=0, column=4, rowspan=5)
    canvas._tkcanvas.grid(row=0, column=4, rowspan=5)


def ping(host):
    param = '-n'
    try:
        command = ['ping', param, '1', host]
        res = str(subprocess.check_output(command))
    except subprocess.CalledProcessError:
        print("ERROR")
        remove_test_from_db(cur.lastrowid)
        return 9999

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
        if y > 9000:
            count = 9999
            return
        count = count + 1
        insert_ping_to_db(ip_id, count, y)
        x_vals.append(count)
        y_vals.append(y)

        a.clear()
        a.plot(x_vals, y_vals, '-o')
    else:
        start = 0
        ani.event_source.stop()
        buttonText.set("Start")
        con.commit()
        populate_history(listBox)


def Start():
    global host, timer, start, ani, count, f, x_vals, y_vals, ip_id
    if buttonText.get() == "Stop":
        start = 0
        ani.event_source.stop()
        buttonText.set("Start")
        con.commit()
        return
    buttonText.set("Stop")
    if (start == 0):
        start = 1
        a.clear()
        x_vals = []
        y_vals = []
        count = 0

        host = iphostEntry.get()
        timer = int(timerEntry.get())

        ip_id = insert_test_to_db(host)
        ani = FuncAnimation(f, animate, interval=1000)
        # anims.append(ani)

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


def change_current_select(i):
    global current_select
    current_select = listBox.get(listBox.curselection())
    return


app = tk.Tk()
app.geometry("1000x550")
app.resizable(False, False)
buttonText = tk.StringVar()
buttonText.set("Start")

iphostEntry = tk.Entry(app, width=40, borderwidth=5)
iphostEntry.grid(row=1, column=0)
iphostEntry.insert(0, "")

label2 = tk.Label(app, text="Nazwa hosta / Adres IP", width=40)
label2.grid(row=0, column=0)

start_button = tk.Button(app, textvariable=buttonText, command=Start, width=60)
start_button.grid(row=2, column=0, columnspan=4)

label3 = tk.Label(app, text="Średni czas odpowiedzi: ", width=50)
label3.grid(row=5, column=4)

label1 = tk.Label(app, text="Czas trwania pomiaru (s)", width=20)
label1.grid(row=0, column=1, columnspan=3)

label5 = tk.Label(app, text="Historia poprzednich pomiarów", width=50)
label5.grid(row=3, column=0, columnspan=2)

history = tk.Frame(app, width=100, height=300)
history.grid(row=4, column=0, columnspan=2)

listBox = tk.Listbox(history, width=55, height=20)
listBox.grid(row=0, column=0, columnspan=2)
listBox.bind("<<ListboxSelect>>", change_current_select)

scrollbar = tk.Scrollbar(history, orient=tk.VERTICAL)
scrollbar.grid(row=0, column=2, sticky=tk.N+tk.S)

listBox.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=listBox.yview)


show_button = tk.Button(app, text="Wyświetl pomiar", command=show_plot, width=25)
show_button.grid(row=5, column=0, columnspan=1)

delete_button = tk.Button(app, text="Usuń pomiar", command=remove_selected_from_db, width=25)
delete_button.grid(row=5, column=1, columnspan=1)

populate_history(listBox)

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
    if len(y_vals) != 0:
        average = round(sum(y_vals) / len(y_vals), 2)
        label3['text'] = "Średni czas odpowiedzi: " + str(average) + "ms"
        app.after(1000, update)
    else:
        label3['text'] = "Średni czas odpowiedzi: 0ms"
        app.after(1000, update)


app.after(1000, update)

app.mainloop()

con.close()
