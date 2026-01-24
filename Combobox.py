import tkinter
from tkinter import ttk

class Combobox(ttk.Combobox):

    def __init__(self, root, name, x, y, val, vals):
        self.var = tkinter.StringVar()
        self.var.set(val)
        super().__init__(root, height = 1, width = 41, textvariable = self.var, state = "readonly")
        self.name = name
        self.place(anchor = "nw", x = x, y = y)
        self["values"] = tuple(vals)


    def getVal(self):
        return self.var.get()