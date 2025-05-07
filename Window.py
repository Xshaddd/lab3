from tkinter import *
from tkinter import ttk

def Default(name: str) -> Tk:
    root = Tk()
    root.title(name)
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    return root