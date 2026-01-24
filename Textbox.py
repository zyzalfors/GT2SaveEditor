import tkinter

class Textbox(tkinter.Text):

    def __init__(self, root, name, x, y, val, dis):
        super().__init__(root, height = 1, width = 33, wrap = tkinter.NONE)
        self.name = name
        self.place(anchor = "nw", x = x, y = y)
        self.insert(tkinter.END, val)
        self.bind("<Return>", lambda _: "break")

        if dis:
            self.config(state = "disabled")