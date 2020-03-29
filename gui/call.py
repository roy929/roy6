from tkinter import *
from tkinter.ttk import *
from threading import Thread
import time
from gui.gui_methods import pop_up_message, center_window
from connection import conn
from data import voice
from winsound import PlaySound, SND_LOOP, SND_ASYNC, SND_PURGE

ring = 'ring.wav'


class Call:
    USER_NAME = ""
    cancel = False

    def __init__(self, win, user_name):
        self.USER_NAME = user_name
        self.win = win
        self.win.title('VoiceChat')
        self.style = Style(self.win)
        self.style.configure('TLabel', font=('Ariel', 20), foreground='magenta')
        self.mainF = Frame(self.win)
        self.callF = Frame(self.win)
        self.chatF = Frame(self.win)
        self.text1 = Label(self.callF, style='TLabel')
        self.text2 = Label(self.chatF, style='TLabel')
        self.users = Listbox(self.mainF, fg='green', font=('Ariel', 12))
        self.target_name = Entry(self.mainF, font=('Ariel', 12))
        center_window(self.win)
        self.set_users_list()

    def main(self):
        self.set()
        self.win.mainloop()

    # sets the widgets on the frames
    def set(self):
        # mainF
        Label(self.mainF, text='Call to', font=('Ariel', 20), foreground='magenta').pack(side=TOP)
        self.target_name.pack()
        Button(self.mainF, text='Call', command=self.pre_call).pack()
        Label(self.mainF, text='Users', font=('Ariel', 18), foreground='blue').pack()
        self.users.pack()
        self.users.bind_all('<<ListboxSelect>>', self.to_entry)
        self.mainF.bind_all('<Return>', self.pre_call)
        self.target_name.focus_set()
        self.mainF.pack()
        # callF
        self.text1.pack(side=TOP)
        Button(self.callF, text='Cancel Call', command=self.stop_calling).pack()
        # chatF
        self.text2.pack()
        Button(self.chatF, text='End Chat', command=self.close_chat).pack()

    # create list of users
    def set_users_list(self):
        self.users.delete(0, END)
        users = conn.user_lists()
        for user in users:
            if user != self.USER_NAME:
                self.users.insert(END, user)
        if self.users.size() < 10:
            self.users.configure(height=self.users.size())

    # put a user in entry
    def to_entry(self, event=None):
        index = self.users.curselection()
        name = self.users.get(index)
        self.target_name.delete(0, END)
        self.target_name.insert(0, name)

    # checks if name valid, if so runs call
    def pre_call(self, event=None):
        target = self.target_name.get()
        self.target_name.delete(0, END)
        if len(target) > 2 and target != self.USER_NAME:
            user_ip = conn.get_user_ip(target)
            if user_ip:  # checks if the user exists
                # start call
                t = Thread(target=self.call_now, args=(target,))
                t.start()
            else:
                pop_up_message("sorry, the user '{0}' is not registered yet".format(target))
        elif len(target) < 3:
            pop_up_message('sorry, the name is too short, at least 3 characters')
        else:
            pop_up_message("you can't call yourself")

    # checks if target agreed to chat
    def wait_for_answer(self, target, timeout=1):
        max_time = time.time() + 60 * timeout  # 1 minutes from now
        # check if 'calling' changed to 'call'
        PlaySound(ring, SND_LOOP + SND_ASYNC)
        while True:
            if self.cancel:
                result = 'canceled'
                break
            if time.time() > max_time:
                result = 'timed_out'
                break
            if conn.is_in_chat(self.USER_NAME, target) == 'call':
                result = 'accepted'
                break
            time.sleep(0.5)
        PlaySound(None, SND_PURGE)
        return result

    # calls and handle the call
    def call_now(self, target):
        self.text1.configure(text=f'Calling {target}...')
        self.text2.configure(text=f'In chat with {target}')
        self.mainF.forget()
        self.callF.pack()
        is_posted = conn.call(self.USER_NAME, target)
        if is_posted:
            print('call posted')
            result = self.wait_for_answer(target, 2)
            if result == 'accepted':
                self.callF.forget()
                self.chatF.pack()
                print('call accepted')
                voice.start()  # start chat
            else:
                conn.stop_calling(self.USER_NAME)
                conn.stop_chat(self.USER_NAME)

                if result == 'timed_out':  # waited too long for response from the call target
                    pop_up_message("call canceled, didn't receive answer in time")
                    print("call canceled, didn't receive answer in time")

        else:  # error, call already exists, handling
            conn.stop_calling(self.USER_NAME)
            self.call_now(target)

        # reset page
        self.cancel = False
        self.callF.forget()
        self.chatF.forget()
        self.mainF.pack()

    # closes chat and resets to main frame
    def close_chat(self):
        conn.stop_chat(self.USER_NAME)
        voice.end()
        self.chatF.forget()
        self.mainF.pack()

    # cancels call
    def stop_calling(self):
        self.cancel = True


if __name__ == '__main__':
    window = Tk()
    my_name = 'roy'
    c = Call(window, my_name)
    c.main()
