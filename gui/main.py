from tkinter import *
from tkinter.ttk import *
from gui.login import Login
from gui.register import Register
from gui.gui_methods import center_window


class Main:

    def __init__(self, win):
        self.win = win
        self.win.title('VoiceChat')
        self.style = Style(self.win)
        self.frame = Frame(self.win)
        self.button_login = Button(self.frame, text='login', command=self.login)
        self.button_register = Button(self.frame, text='register', command=self.register)
        center_window(self.win)

    def main(self):
        self.button_login.grid(row=0)
        self.button_register.grid(row=1)
        self.frame.pack()

    def login(self):
        self.frame.destroy()
        Login(self.win).main()

    def register(self):
        self.frame.destroy()
        Register(self.win).main()


if __name__ == '__main__':
    window = Tk()
    f = Main(window)
    f.main()
    window.mainloop()
