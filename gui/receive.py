from tkinter import *
from tkinter.ttk import *
from threading import Thread
import time
from connection import conn
from gui.gui_methods import center_window
from data import voice


class Receive:
    USER_NAME = ""

    def __init__(self, win, user_name):
        self.USER_NAME = user_name
        self.win = win
        self.win.title('Receive')
        self.style = Style(self.win)
        self.mainF = Frame(self.win)
        self.callF = Frame(self.win)
        self.chatF = Frame(self.win)
        self.text1 = Label(self.callF, font=('Ariel', 20), foreground='magenta')
        self.text2 = Label(self.chatF, font=('Ariel', 20), foreground='magenta')
        center_window(self.win)

    def set(self):
        # grid & pack
        # mainF:
        Label(self.mainF, text='waiting for a call', font=('Ariel', 20), foreground='magenta').pack()
        # callF:
        self.text1.pack()
        self.callF.bind_all('<Return>', self.yes)
        yes = Button(self.callF, text='yes', command=self.yes)
        yes.focus_set()
        yes.pack()
        Button(self.callF, text='no', command=self.no).pack()
        # chatF:
        self.text2.pack()
        Button(self.chatF, text='End Chat', command=self.cancel).pack()

    def main(self):
        self.set()
        self.mainF.pack()
        wait_thread = Thread(target=self.wait_for_a_call)
        wait_thread.start()
        self.win.mainloop()

    def wait_for_a_call(self):
        while True:
            if conn.look_for_call(self.USER_NAME):
                break
            time.sleep(0.5)

        user = conn.get_src_name(self.USER_NAME)
        print(user, 'called')

        self.mainF.forget()
        self.callF.pack()
        self.text1.configure(text=f'you got a call from {user}\ndo you want to agree?')
        self.text2.configure(text=f'In chat with {user}')

    def cancel(self):
        self.chatF.forget()
        self.mainF.pack()
        conn.stop_chat(self.USER_NAME)
        print('end')
        wait_thread = Thread(target=self.wait_for_a_call)
        wait_thread.start()

    def yes(self):
        self.callF.forget()
        self.chatF.pack()
        user = conn.get_src_name(self.USER_NAME)
        if conn.accept(user, self.USER_NAME):
            end_thread = Thread(target=self.check_if_chat_over, args=[user])
            end_thread.start()
            voice_thread = Thread(target=voice.start)
            voice_thread.start()

    def no(self):
        self.callF.forget()
        self.mainF.pack()
        conn.stop_chat(self.USER_NAME)
        wait_thread = Thread(target=self.wait_for_a_call)
        wait_thread.start()

    def check_if_chat_over(self, user):
        while True:
            time.sleep(0.5)
            if not conn.is_in_chat(user, self.USER_NAME):
                voice.end()
                break


if __name__ == '__main__':
    window = Tk()
    r = Receive(window, 'kkk')
    r.main()
