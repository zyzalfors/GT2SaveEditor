import tkinter

class Checkbox(tkinter.Checkbutton):

    def __init__(self, root, label, checked):
        self.var = tkinter.IntVar()
        self.var.set(checked)
        super().__init__(root, text = label, variable = self.var, onvalue = 1, offvalue = 0)
        self.name = label


    def isChecked(self):
        return self.var.get()