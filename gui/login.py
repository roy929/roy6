from tkinter import *
from tkinter.ttk import *
from gui.gui_methods import pop_up_message, center_window
from gui.call import Call
from connection import flask_requests


class Login:
    MY_USER_NAME = ""

    def __init__(self, win=None):
        if win:
            self.win = win
        else:
            self.win = Tk()
        self.win.title('Login')
        self.style = Style(self.win)
        self.frame = Frame(self.win)
        self.entry_name = Entry(self.frame)
        self.entry_pas = Entry(self.frame, show='*')
        center_window(self.win)

    def main(self):
        # self.win.geometry('500x500')
        name = Label(self.frame, text='Name')
        pas = Label(self.frame, text='Password')
        enter = Button(self.frame, text='Enter', command=self.handle)
        self.frame.bind_all('<Return>', self.handle)

        self.entry_name.focus_set()

        # grid & pack
        name.grid(row=0, sticky=E)
        pas.grid(row=1, sticky=E)
        self.entry_name.grid(row=0, column=1)
        self.entry_pas.grid(row=1, column=1)
        enter.grid()
        self.frame.pack()
        self.win.mainloop()

    def handle(self, event=None):
        name = self.entry_name.get()
        pas = self.entry_pas.get()

        is_connected = flask_requests.login(name, pas)
        if is_connected:
            self.MY_USER_NAME = name
            pop_up_message("you're in, {}".format(self.MY_USER_NAME))
            # open chat mainpage
            self.open_mainpage()
        else:
            self.entry_name.delete(0, len(name))
            self.entry_pas.delete(0, len(pas))
            pop_up_message("name or password is incorrect")

    def open_mainpage(self):
        self.frame.destroy()
        mp = Call(self.MY_USER_NAME, self.win)
        mp.main()


if __name__ == '__main__':
    login = Login()
    login.main()
