___author___ = "Jian Wu"
___email___ = "jian.wu@tamu.edu"


import Tkinter as tk

import collections
import thread
import socket
import math
import serial
import Queue
import struct
import threading
from reg_UI import reg_UI

WATCH_NUM = 5
DEF_MACADDR = ['2KTR', '2KZ8', '2KZ9', '2MJS', '2KTM']

class ThreadedClient:

    def __init__(self, master):
        self.name_list = ["Jian", "William", "Peiming", "Viswam", "Bassem", "Ali A", "Xien", "Ning", "Kim", "Zach"]
        self.master = master
        self.watch_queue = [collections.deque(maxlen=100) for x in range(WATCH_NUM)]
        self.motion_queue = collections.deque(maxlen=100)
        self.gui = reg_UI(master, self.name_list, self.motion_queue, self.watch_queue)

        # Start smart watch server and start to receive data from all clients.
        UDP_IP = '192.168.0.129'
        UDP_PORT = 4570
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((UDP_IP, UDP_PORT))
        thread.start_new_thread(self.read_watch, ())


        # Start to receive data from MotionNet.
        self.serial = serial.Serial("COM3", 115200, timeout=5)
        self.data = [0 for x in range(50)]
        self.data_package = Queue.Queue(maxsize=50)
        self.parsed_data = [0 for x in range(6)]
        thread.start_new_thread(self.read_motion, ())
        self.lock = thread.allocate_lock()
        self.periodicCall()

        # five timer to track the health status of watch
        self.timers = [threading.Timer(3.0, self.timeout, [DEF_MACADDR[i]]) for i in range(len(DEF_MACADDR))]
        # every 25 sample (1s) to update Timer.
        self.counter = [0 for i in range(WATCH_NUM)]

    def timeout(self, watch_id):
        self.gui.update_battery_table(watch_id, "no")
        index = 0
        for i in range(len(DEF_MACADDR)):
            if watch_id == DEF_MACADDR[i]:
                index = i
        self.timers[index].cancel()

    def periodicCall(self):
        self.gui.processIncoming()
        self.master.after(50, self.periodicCall)

    def read_watch(self):
        while True:
            # packet format: str(device_id + " " + packet_type +  " " + gyro_mag)
            data, addr = self.sock.recvfrom(1024)

            # start all five timers to monitor sensor data
            for i in range(WATCH_NUM):
                self.timers[i].start()

            #print data
            parsed_data = data.split(' ')
            if (parsed_data[1] == 'w'):
                gyro_mag = float(parsed_data[2])
                for i in range(WATCH_NUM):
                    if (parsed_data[0] == DEF_MACADDR[i]):
                        self.counter[i] = self.counter[i] + 1
                        if (self.counter[i] == 25):
                            self.counter[i] = 0
                            self.timers[i].cancel()
                            self.timers[i] = threading.Timer(3.0, self.timeout, [parsed_data[0]])
                            self.timers[i].start()
                        self.lock.acquire()
                        self.watch_queue[i].append(gyro_mag)
                        self.lock.release()
            if(parsed_data[1] == 'b'):
                battery_life = parsed_data[2]
                for i in range(WATCH_NUM):
                    if (parsed_data[0] == DEF_MACADDR[i]):
                        self.lock.acquire()
                        self.watch_battery[i] = int(battery_life)
                        self.lock.release()
                        self.gui.update_battery_table(parsed_data[0], battery_life, "yes")


    def read_motion(self):
        while True:
            while (self.data_package.qsize() < 50):
                self.data_package.put(self.serial.read(1))
            i = 1
            while (i == 1):
                self.data[0] = self.data_package.get()
                if (ord(self.data[0]) == 16):
                    self.data[1] = self.data_package.get()
                    if (ord(self.data[1]) == 1):
                         j = 1
                         k = 2
                         while (j == 1):
                            self.data[k] = self.data_package.get()
                            if (ord(self.data[k]) == 16):
                                self.data[k + 1] = self.data_package.get()
                                if (ord(self.data[k + 1]) == 4):
                                    j = 0
                                    i = 0
                            k = k + 1
            for l in range(1, 7):
                datastr = self.data[l*2] + self.data[l*2 + 1]
                self.parsed_data[l-1] = struct.unpack(">h", datastr)[0]
            gyro_x = self.parsed_data[3]/32.75
            gyro_y = self.parsed_data[4]/32.75
            gyro_z = self.parsed_data[5]/32.75

            gyro_mag = math.sqrt(gyro_x*gyro_x + gyro_y*gyro_y + gyro_z*gyro_z)
            self.lock.acquire()
            self.motion_queue.append(gyro_mag)
            self.lock.release()

if __name__ == "__main__":
    root = tk.Tk()
    client = ThreadedClient(root)
    root.mainloop()


