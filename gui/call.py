from tkinter import *
from tkinter.ttk import *
from threading import Thread
import time
from gui.gui_methods import pop_up_message, center_window
from connection import flask_requests
from data import voice
from winsound import PlaySound, SND_LOOP, SND_ASYNC, SND_PURGE

ring = 'ring.wav'


class Call:
    USER_NAME = ""
    cancel = False
    timed_out = False

    def __init__(self, win, my_user_name):
        self.USER_NAME = my_user_name
        self.win = win
        self.win.title('VoiceChat')
        self.style = Style(self.win)
        self.start_frame = Frame(self.win)
        self.in_chat_frame = Frame(self.win)
        self.text1 = Label(self.start_frame, text='Call to', font=('Ariel', 20), foreground='magenta')
        self.text2 = Label(self.in_chat_frame, font=('Ariel', 20), foreground='magenta')
        self.text3 = Label(self.start_frame, text='Users', font=('Ariel', 18), foreground='blue')
        self.users = Listbox(self.start_frame, fg='green', font=('Ariel', 12))
        self.user_to_call = Entry(self.start_frame, font=('Ariel', 12))
        self.callB = Button(self.start_frame, text='Call', command=self.pre_call)
        self.cancelB = Button(self.in_chat_frame, text='Cancel Call', command=self.stop_calling)
        self.end_chatB = Button(self.in_chat_frame, text='End Chat', command=self.close_chat)
        center_window(self.win)
        self.set_users_list()

    # packing and set up
    def main(self):
        # frame1
        self.text1.pack(side=TOP)
        self.user_to_call.pack()
        self.callB.pack()
        self.text3.pack()
        self.users.pack()
        self.users.bind_all('<<ListboxSelect>>', self.put_in_call)
        self.start_frame.bind_all('<Return>', self.pre_call)
        self.user_to_call.focus_set()
        self.start_frame.pack()
        # frame2
        self.text2.pack(side=TOP)
        self.cancelB.pack()

        self.win.mainloop()

    def set_users_list(self):
        self.users.delete(0, END)
        users = flask_requests.user_lists()
        for user in users:
            if user != self.USER_NAME:
                self.users.insert(END, user)
        if self.users.size() < 10:
            self.users.configure(height=self.users.size())

    def put_in_call(self, event=None):
        index = self.users.curselection()
        name = self.users.get(index)
        self.user_to_call.delete(0, END)
        self.user_to_call.insert(0, name)

    def pre_call(self, event=None):
        user_name = self.user_to_call.get()
        self.user_to_call.delete(0, END)
        if len(user_name) > 2 and user_name != self.USER_NAME:
            user_ip = flask_requests.get_user_ip(user_name)
            if user_ip:  # checks if the user exists
                # start call
                t = Thread(target=self.call_now, args=(user_name,))
                t.start()
            else:
                pop_up_message("sorry, the user '{0}' is not registered yet".format(user_name))
        elif len(user_name) < 3:
            pop_up_message('sorry, the name is too short, at least 3 characters')
        else:
            pop_up_message("you can't call yourself")

    def wait_for_answer(self, user_name, timeout=1):
        max_time = time.time() + 60 * timeout  # 1 minutes from now
        # check if 'calling' changed to 'call'
        PlaySound(ring, SND_LOOP + SND_ASYNC)
        while not self.cancel:
            if time.time() > max_time:
                self.timed_out = True
                return False
            if flask_requests.is_in_chat(self.USER_NAME, user_name) == 'call':
                return True
            time.sleep(0.5)
        PlaySound(None, SND_PURGE)
        return False

    def call_now(self, user_name):
        self.text2.configure(text=f'Calling {user_name}...')
        self.start_frame.forget()
        self.in_chat_frame.pack()
        is_posted = flask_requests.call(self.USER_NAME, user_name)
        if is_posted:
            print('call posted')
            if self.wait_for_answer(user_name, 2):
                print('call accepted')
                self.cancelB.forget()
                self.text2.configure(text=f'In chat with {user_name}')
                self.end_chatB.pack()
                voice.start()  # start chat
                # set frame back
                self.cancelB.pack()
                self.end_chatB.forget()
            elif self.timed_out:  # # waited too long for response from the call target
                flask_requests.stop_calling(self.USER_NAME)
                # waited too long for response from the call target
                pop_up_message('call canceled, waiting too long for answer')
                print('call canceled, waiting too long for answer')
        else:  # call already exists, handling
            flask_requests.stop_calling(self.USER_NAME)
            self.call_now(user_name)

        # reset page
        self.cancel = False
        self.timed_out = False
        self.in_chat_frame.forget()
        self.start_frame.pack()

    def close_chat(self):
        flask_requests.stop_chat(self.USER_NAME)
        voice.end()
        self.in_chat_frame.forget()
        self.start_frame.pack()

    def stop_calling(self):
        flask_requests.stop_calling(self.USER_NAME)
        self.cancel = True


if __name__ == '__main__':
    window = Tk()
    my_name = 'roy'
    conn = Call(window, my_name)
    conn.main()
