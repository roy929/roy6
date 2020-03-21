import requests
import time
import socket

# hostname = 'DESKTOP-EVCG5AF'
hostname = socket.gethostname()  # '127.0.0.1'
server_ip = socket.gethostbyname(hostname)
server_port = 5000
flask_url = f'http://{server_ip}:{server_port}'


# returns ip or 0 if user doesnt exist
def get_user_ip(name):
    data = {'name': name}
    r = requests.get(flask_url + '/get_ip', data=data)
    return r.json()  # r.status_code


def login(name, pas):
    data = {'name': name, 'password': pas}
    r = requests.get(flask_url + '/login', data=data)
    if r.json() == 'True':
        return True
    return False


def register(name, pas):
    data = {'name': name, 'password': pas}
    r = requests.post(flask_url + '/register', data=data)
    if r.json() == 'True':
        return True
    return False


# post calling
def call(src_name, dst_name):
    new_call = {'src': src_name, 'operation': 'calling', 'dst': dst_name}
    r = requests.post(flask_url + '/call', data=new_call)
    # print(r.json())  # r.status_code
    if r.json() == 'True':
        return True
    return False


# change to calling to call
def accept(src_name, dst_name):
    new_call = {'src': src_name, 'operation': 'call', 'dst': dst_name}
    r = requests.put(flask_url + '/accept', data=new_call)
    return r.json()
    # print(r.json())  # r.status_code


def look_for_call(dst_name):
    check_call = {'operation': 'calling', 'dst': dst_name}
    r = requests.get(flask_url + '/check', data=check_call)
    return r.json()  # src name || ""


def who_is_calling(dst_name):
    name = look_for_call(dst_name)
    if name:
        return name


# check if call accepted or if call still alive
def is_in_chat(src, dst):
    data = {'src': src, 'dst': dst}
    r = requests.get(flask_url + '/check', data=data)
    # json = operation
    return r.json()  # operation


# when calling
def stop_calling(name):
    msg = {'name': name, 'operation': 'calling'}
    r = requests.delete(flask_url + "/stop_call", data=msg)
    print(r.json())  # r.status_code


# when in chat
def stop_chat(name):
    check_call = {'name': name, 'operation': 'call'}
    r = requests.delete(flask_url + "/stop_call", data=check_call)
    print(r.json())  # r.status_code


if __name__ == '__main__':
    my_name = 'kkk'
    while True:
        if look_for_call(my_name):
            break
    user = who_is_calling(my_name)
    print(user)
    accept(my_name, user)

    time.sleep(7)
    stop_chat(my_name)
