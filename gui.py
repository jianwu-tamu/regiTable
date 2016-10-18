import Tkinter as tk

class UserInterface:

    def __init__(self, names, callback, column = 2):
        self.__names__ = names;
        self.__column__ = column
        self.__callback__ = callback;
        
    def run(self):
        root = tk.Tk()
        for i in range(0, len(self.__names__)):
            tk.Button(root, command = lambda name = self.__names__[i] : self.__callback__(name), text = self.__names__[i], height = 2, width = 10, font=("Arial",30,"bold")).\
                     grid(row = i / self.__column__, column = i % self.__column__, sticky=tk.N+tk.E+tk.S+tk.W, padx = 10, pady = 2)
        root.mainloop();


def callback(content):
    print content

    
ui = UserInterface(['peiming', 'william', 'jian', 'Viswan', 'Bassam', 'Ali'], callback)
ui.run()
