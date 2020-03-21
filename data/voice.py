import socket
import pyaudio
from threading import Thread


# record
CHUNK = 1024  # 512
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 20000
# socket
SERVER_PORT = 50002
SERVER_IP = "127.0.0.1"


# connect to server and start stream
def conn(server_ip, server_port):
    global s, receive_stream, send_stream, run_chat

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((server_ip, server_port))
    run_chat = True

    p = pyaudio.PyAudio()

    receive_stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer=CHUNK)
    send_stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

    print("Voice chat running")


def receive_data():
    while run_chat:
        try:
            data = s.recv(1024)
            receive_stream.write(data)
        except:
            pass


def send_data():
    while run_chat:
        try:
            data = send_stream.read(CHUNK)
            s.sendall(data)
        except:
            pass


def start():
    conn(SERVER_IP, SERVER_PORT)
    recv = Thread(target=receive_data)
    send = Thread(target=send_data)
    recv.start()
    send.start()
    recv.join()
    send.join()
    s.close()
    print('voice closed')


def end():
    global run_chat
    run_chat = False
