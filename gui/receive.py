from tkinter import *
from tkinter.ttk import *
from threading import Thread
import time
from connection import flask_requests
from gui.gui_methods import center_window
from data import voice


class Receive:
    MY_USER_NAME = ""

    def __init__(self, win, my_user_name):
        self.MY_USER_NAME = my_user_name
        self.win = win
        self.win.title('Receive')
        self.style = Style(self.win)
        self.main_frame = Frame(self.win)
        self.called_frame = Frame(self.win)
        self.in_chat_frame = Frame(self.win)
        self.msg1 = Label(self.main_frame, text='waiting for a call')
        self.msg2 = Label(self.called_frame)
        self.msg3 = Label(self.in_chat_frame, text='in chat')
        self.cancel_button = Button(self.in_chat_frame, text='cancel', command=self.cancel)
        self.yes_button = Button(self.called_frame, text='yes', command=self.yes)
        self.no_button = Button(self.called_frame, text='no', command=self.no)
        center_window(self.win)

    def set(self):
        # grid & pack
        # # frame 1:
        self.msg1.pack()
        # frame 2:
        self.msg2.pack()
        self.called_frame.bind_all('<Return>', self.yes)
        self.yes_button.focus_set()
        self.yes_button.pack()
        self.no_button.pack()
        # frame 3:
        self.msg3.pack()
        self.cancel_button.pack()

    def main(self):
        self.set()  # need to run only one time
        self.main_frame.pack()
        wait_thread = Thread(target=self.wait_for_a_call)
        wait_thread.start()
        self.win.mainloop()

    def wait_for_a_call(self):
        while True:
            if flask_requests.look_for_call(self.MY_USER_NAME):
                break
            time.sleep(0.5)

        user = flask_requests.get_src_name(self.MY_USER_NAME)
        print(user, 'called')

        self.main_frame.forget()
        self.called_frame.pack()
        self.msg2.configure(text=f'you got a call from {user}')

    def cancel(self):
        self.in_chat_frame.forget()
        self.main_frame.pack()
        flask_requests.stop_chat(self.MY_USER_NAME)
        print('end')
        wait_thread = Thread(target=self.wait_for_a_call)
        wait_thread.start()

    def yes(self):
        self.called_frame.forget()
        self.in_chat_frame.pack()
        user = flask_requests.get_src_name(self.MY_USER_NAME)
        if flask_requests.accept(user, self.MY_USER_NAME):
            end_thread = Thread(target=self.check_if_chat_over, args=[user])
            end_thread.start()
            voice_thread = Thread(target=voice.start)
            voice_thread.start()

    def no(self):
        self.called_frame.forget()
        self.main_frame.pack()
        flask_requests.stop_chat(self.MY_USER_NAME)
        wait_thread = Thread(target=self.wait_for_a_call)
        wait_thread.start()

    def check_if_chat_over(self, user):
        while True:
            time.sleep(0.5)
            if not flask_requests.is_in_chat(user, self.MY_USER_NAME):
                voice.end()
                break


if __name__ == '__main__':
    window = Tk()
    r = Receive(window, 'kkk')
    r.main()
