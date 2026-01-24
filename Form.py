import tkinter
from tkinter import filedialog
from tkinter import ttk
from Checkbox import Checkbox
from Textbox import Textbox
from Combobox import Combobox
from RaCSave import RaCSave

class Form(tkinter.Tk):
    TYPES = ("bin file", "*.bin")
    SHIFT = 21


    def __init__(self):
        super().__init__()
        self.save = None
        self.labels = []
        self.textboxes = []
        self.comboboxes = []
        self.checkboxes = []
        self.notebook = None
        self.initGUI()


    def initGUI(self):
        self.title("RaC Save Editor")
        self.geometry("410x700")
        self.resizable(False, False)

        menuBar = tkinter.Menu(self)

        fileMenu = tkinter.Menu(menuBar, tearoff = False)
        fileMenu.add_command(label = "Open", command = self.open)
        fileMenu.add_command(label = "Update", command = self.update)
        fileMenu.add_command(label = "Close and update", command = self.closeAndUpdate)
        fileMenu.add_command(label = "Close", command = self.close)
        fileMenu.add_command(label = "Exit", command = self.destroy)

        menuBar.add_cascade(label = "File", menu = fileMenu)
        self.config(menu = menuBar)


    def open(self):
        path = tkinter.filedialog.askopenfilename(title = "Open", filetypes = [self.TYPES])
        if path == "":
            return

        game = tkinter.simpledialog.askstring(title = None, prompt = f"Enter game ({', '.join(RaCSave.GAMES)}):")
        if game:
            game = game.strip().lower()

        if not game in RaCSave.GAMES:
            tkinter.messagebox.showerror("Error", "Invalid game.")
            return

        self.save = RaCSave(path, game)

        chunk, check = self.save.checkCrc16()
        if chunk and not check:
            msg = "\n".join(["Invalid checksum:", f"Offset: {chunk[0]}", f"Checksum offset: {chunk[1]}", f"Data offset: {chunk[2]}", f"Data size: {chunk[3]}", "Update save to fix checksum."])
            tkinter.messagebox.showerror("Error", msg)

        self.disposeTab()
        self.initTabs()


    def update(self):
        if not self.save:
            return

        for textbox in self.textboxes:
            self.save.updateValue(textbox.name, textbox.get("1.0", tkinter.END))

        for combobox in self.comboboxes:
            self.save.updateValue(combobox.name, combobox.getVal())

        for checkbox in self.checkboxes:
            self.save.updateItem(checkbox.name, bool(checkbox.isChecked()))

        self.save.update()
        tkinter.messagebox.showinfo("Info", "Save updated.")

        self.disposeTab()
        self.initTabs()


    def closeAndUpdate(self):
        self.update()
        self.close()


    def close(self):
        self.save = None
        self.disposeTab()


    def initTabs(self):
        nb = ttk.Notebook(self)
        nb.pack(expand = True, fill = "both")
        self.notebook = nb

        valuesTab = ttk.Frame(nb)
        nb.add(valuesTab, text = "Values")

        y = 0
        x = 130

        label = tkinter.Label(valuesTab, text = "Path:")
        label.place(anchor = "nw", y = y)
        self.labels.append(label)
        self.textboxes.append(Textbox(valuesTab, "path", x, y, self.save.path, True))

        y += self.SHIFT
        label = tkinter.Label(valuesTab, text = "Game:")
        label.place(anchor = "nw", y = y)
        self.labels.append(label)
        self.textboxes.append(Textbox(valuesTab, "game", x, y, self.save.game, True))

        for value in self.save.getValues():
            name = value[0]
            val = value[1]

            y += self.SHIFT
            label = tkinter.Label(valuesTab, text = name + ":")
            label.place(anchor = "nw", y = y)
            self.labels.append(label)

            if name == "Language":
                self.comboboxes.append(Combobox(valuesTab, name, x, y, val, self.save.LANGUAGES.keys()))

            elif name == "Armor":
                self.comboboxes.append(Combobox(valuesTab, name, x, y, val, self.save.ARMORS.keys()))

            else:
                self.textboxes.append(Textbox(valuesTab, name, x, y, val, False))

        itemsTab = ttk.Frame(nb)
        nb.add(itemsTab, text = "Items")

        y = 0
        items = self.save.getItems()
        for i in range(len(items)):
            check = Checkbox(itemsTab, items[i][0], items[i][1])
            self.checkboxes.append(check)

            if i % 2 == 0:
                check.place(x = 0, y = y + 10 * i)

            else:
                check.place(x = 145, y = y + 10 * (i - 1))


    def disposeTab(self):
        for label in self.labels:
            label.destroy()

        self.labels.clear()

        for textbox in self.textboxes:
            textbox.destroy()

        self.textboxes.clear()

        for combobox in self.comboboxes:
            combobox.destroy()

        self.comboboxes.clear()

        for checkbox in self.checkboxes:
            checkbox.destroy()

        self.checkboxes.clear()

        if self.notebook:
            self.notebook.destroy()