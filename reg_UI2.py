import Tkinter as tk

## This class pop up a new window that confirm the registration information.
class reg_UI2:

    pair_status = False
    name = " "

    def __init__(self, master, name):
        reg_UI2.name = name
        self.master = master
        var = "You are registrating as " + name
        self.text = tk.Message(self.master, text=var, width=800, font=("Arial",30,"bold"))
        self.text.pack()
        self.confirm_button = tk.Button(self.master, text="confirm", width=20, font=("Arial",30,"bold"))
        self.confirm_button.pack()
        self.confirm_button.bind('<Button-1>', self.update_table)
        self.cancel_button = tk.Button(self.master, text="cancel", command=self.close_windows, width=20, font=("Arial",30,"bold"))
        self.cancel_button.pack()

    def close_windows(self):
        self.master.destroy()
        return

    def update_table(self, event):
        reg_UI2.pair_status = True
        self.master.destroy()
        return
