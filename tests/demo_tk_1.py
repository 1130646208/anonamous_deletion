import tkinter as tk
from tkinter import *
import json

root = tk.Tk()
frame1 = tk.Frame(root).grid()
frame2 = tk.Frame(root).grid()
data = {'name': "John", 'age': 31, 'city': "New York"}
text = json.dumps(data, indent=2)



txt = tk.Text(frame2, font="Times32")
txt.grid(row=1, column=0, columnspan=3)
sb = tk.Scrollbar(frame2)
sb.grid(row=1, column=4, sticky=S + W + E + N)
txt.config(yscrollcommand=sb.set)
sb.config(command=txt.yview)

def fun():
    txt.insert('end', text)
    txt.insert('end', text)
    txt.insert('end', text)
    txt.insert('end', text)
    txt.insert('end', text)
    return 3

b1 = tk.Button(frame1, text='按钮1', fg='black', command=fun)
tk.Button(frame1, text='按钮2', fg='black', command=None).grid(row=0, column=1)
tk.Button(frame1, text='按钮3', fg='black', command=None).grid(row=0, column=2)

b1.grid(row=0, column=0)





root.mainloop()
