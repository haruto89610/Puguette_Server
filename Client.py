import socket
import sys
import threading
import struct
import time
from multiprocessing import Queue
import multiprocessing
import numpy as np
from XInput import *

HOST = "10.192.172.215"  # The server's hostname or IP addressr
PORT = 65432  # The port used by the server
data = ""

protocol = {
    "LEFT_JOYSTICK": [0, 0],
    "RIGHT_JOYSTICK": [0, 0],
    "LEFT_TRIGGER": 0,
    "RIGHT_TRIGGER": 0,
    "LEFT_THUMB": False,
    "RIGHT_THUMB": False,
    "LEFT_SHOULDER": False,
    "RIGHT_SHOULDER": False,
    "BACK": False,
    "START": False,
    "DPAD_LEFT": False,
    "DPAD_RIGHT": False,
    "DPAD_UP": False,
    "DPAD_DOWN": False,
    "A": False,
    "B": False,
    "X": False,
    "Y": False
}
protocol_format = ">6f14?"

queue = Queue()


def controller_input():
    global data, protocol
    frequency = 0.05
    while True:
        loop_enter = time.perf_counter()
        for event in get_events():
            if event.type == EVENT_STICK_MOVED:
                if event.stick == LEFT:
                    protocol["LEFT_JOYSTICK"][0] = get_thumb_values(get_state(event.user_index))[0][1] / 40
                    protocol["LEFT_JOYSTICK"][1] = get_thumb_values(get_state(event.user_index))[0][0] / 20
                    current_input = 0
                elif event.stick == RIGHT:
                    protocol["RIGHT_JOYSTICK"][0] = get_thumb_values(get_state(event.user_index))[1][0] / 2
                    protocol["RIGHT_JOYSTICK"][1] = get_thumb_values(get_state(event.user_index))[1][1] / 2
                    current_input = 1

            elif event.type == EVENT_TRIGGER_MOVED:
                if event.trigger == LEFT:
                    protocol["LEFT_TRIGGER"] = -round(get_trigger_values(get_state(event.user_index))[0] / 10, 2)
                    current_input = 2
                elif event.trigger == RIGHT:
                    protocol["RIGHT_TRIGGER"] = round(get_trigger_values(get_state(event.user_index))[1] / 10, 2)
                    current_input = 3

            elif event.type == EVENT_BUTTON_PRESSED:
                if event.button == "LEFT_THUMB":
                    protocol["LEFT_THUMB"] = True
                elif event.button == "RIGHT_THUMB":
                    protocol["RIGHT_THUMB"] = True

                elif event.button == "LEFT_SHOULDER":
                    protocol["LEFT_SHOULDER"] = True
                elif event.button == "RIGHT_SHOULDER":
                    protocol["RIGHT_SHOULDER"] = True

                elif event.button == "BACK":
                    protocol["BACK"] = True
                elif event.button == "START":
                    protocol["START"] = True

                elif event.button == "DPAD_LEFT":
                    protocol["DPAD_LEFT"] = True
                elif event.button == "DPAD_RIGHT":
                    protocol["DPAD_RIGHT"] = True
                elif event.button == "DPAD_UP":
                    protocol["DPAD_UP"] = True
                elif event.button == "DPAD_DOWN":
                    protocol["DPAD_DOWN"] = True

                elif event.button == "A":
                    protocol["A"] = True
                elif event.button == "B":
                    protocol["B"] = True
                elif event.button == "X":
                    protocol["X"] = True
                elif event.button == "Y":
                    protocol["Y"] = True

            else:
                protocol = {
                    "LEFT_JOYSTICK": [0, 0],
                    "RIGHT_JOYSTICK": [0, 0],
                    "LEFT_TRIGGER": 0,
                    "RIGHT_TRIGGER": 0,
                    "LEFT_THUMB": False,
                    "RIGHT_THUMB": False,
                    "LEFT_SHOULDER": False,
                    "RIGHT_SHOULDER": False,
                    "BACK": False,
                    "START": False,
                    "DPAD_LEFT": False,
                    "DPAD_RIGHT": False,
                    "DPAD_UP": False,
                    "DPAD_DOWN": False,
                    "A": False,
                    "B": False,
                    "X": False,
                    "Y": False
                }

        data = struct.pack(protocol_format,
                           protocol["LEFT_JOYSTICK"][0], protocol["LEFT_JOYSTICK"][1],
                           protocol["RIGHT_JOYSTICK"][0], protocol["RIGHT_JOYSTICK"][1],
                           protocol["LEFT_TRIGGER"], protocol["RIGHT_TRIGGER"],
                           protocol["LEFT_THUMB"], protocol["RIGHT_THUMB"],
                           protocol["LEFT_SHOULDER"], protocol["RIGHT_SHOULDER"],
                           protocol["BACK"], protocol["START"],
                           protocol["DPAD_LEFT"], protocol["DPAD_RIGHT"],
                           protocol["DPAD_UP"], protocol["DPAD_DOWN"],
                           protocol["A"], protocol["B"],
                           protocol["X"], protocol["Y"]
                           )

        queue.put(data)

        print(time.strftime('%Y-%m-%d %H:%M:%S'), struct.unpack(protocol_format, data))

        time_taken = time.perf_counter() - loop_enter
        if time_taken < frequency:
            time.sleep(frequency - time_taken)

def send_data():
    global data
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        print("ready")
        while True:
            s.sendall(queue.get())

controller_thread = threading.Thread(target=controller_input)
send_thread = threading.Thread(target=send_data)

controller_thread.start()
send_thread.start()
