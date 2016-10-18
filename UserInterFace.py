___author___ = "Jian Wu"
___email___ = "jian.wu@tamu.edu"

from functools import partial
import Tkinter as tk
from RegTable import RegTable
import numpy
import heapq
import collections
import thread
import socket
import math
import serial
import Queue
import struct
import tkMessageBox
import ttk

WATCH_NUM = 5
DEF_MACADDR = ['2KTR', '2KZ8', '2KZ9', '2MJS', '2KTM']

class reg_UI:

    def __init__(self, master, name_list, motion_queue, watch_queue):
        self.master = master
        self.motion_queue = motion_queue
        self.watch_queue = watch_queue
        master.title("TerraSwarm Registration")
        self.name_list = name_list
        for i in range(0, len(self.name_list)):
            tk.Button(self.master, command=partial(self.pop_window, self.name_list[i]), text=self.name_list[i], height = 2, width=10, font=("Arial",30,"bold")).\
                     grid(row=i / 2, column = i % 2, sticky=tk.N+tk.E+tk.S+tk.W, padx = 10, pady = 2)
        self.table = RegTable(WATCH_NUM)
        self.lock = thread.allocate_lock()

        # Start to transfer pair information to Presentation PC.
        self.IP_presentation = '192.168.0.113'
        self.PORT_to_presentation = 4569
        self.sock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.battery_table = {}
        for i in range(len(DEF_MACADDR)):
            self.battery_table[DEF_MACADDR[i]] = ("99%", "yes")


    def processIncoming(self):
        print reg_UI2.pair_status
        if (reg_UI2.pair_status == True):
            for i in range(WATCH_NUM):
                if (len(self.watch_queue[i]) == 100):
                    self.lock.acquire()
                    watch_data = list(self.watch_queue[i])
                    self.lock.release()
                    if (numpy.mean(watch_data) > 10):
                        if ((len(self.table.regTable) < WATCH_NUM) and ((DEF_MACADDR[i] not in self.table.regTable.keys()) or (self.table.regTable[DEF_MACADDR[i]] == " "))):
                            self.table.create_table(reg_UI2.name, DEF_MACADDR[i])
                            tkMessageBox.showinfo('confirmation','%s is paired with %s' % (reg_UI2.name, DEF_MACADDR[i]))
                            print reg_UI2.name
                            reg_UI2.pair_status = False
                            if (len(self.table.regTable) > 0):
                                strsend = str(self.table.regTable)
                                print 1,strsend
                                self.sock2.sendto(strsend, (self.IP_presentation, self.PORT_to_presentation))
                        elif ((len(self.table.regTable) == WATCH_NUM) and ((DEF_MACADDR[i] not in self.table.regTable.keys()) or (self.table.regTable[DEF_MACADDR[i]] == " "))):
                            self.table.update_table1(reg_UI2.name, DEF_MACADDR[i])
                            tkMessageBox.showinfo('confirmation','%s is paired with %s' % (reg_UI2.name, DEF_MACADDR[i]))
                            reg_UI2.pair_status = False
                            strsend = str(self.table.regTable)
                            print 2,strsend
                            self.sock2.sendto(strsend, (self.IP_presentation, self.PORT_to_presentation))

        elif (reg_UI2.pair_status == False):
            cov_array = [0 for x in range(WATCH_NUM)]
            self.lock.acquire()
            watch_gyro = self.watch_queue
            MotionNet_gyro = self.motion_queue
            self.lock.release()
            for i in range(WATCH_NUM):
                #print len(watch_gyro[i])
                #print len(MotionNet_gyro)
                if (len(watch_gyro[i]) == 100 and len(MotionNet_gyro) == 100):
                    watch_data = list(watch_gyro[i])
                    motion_data = list(MotionNet_gyro)
                    cov_array[i] = numpy.corrcoef(watch_data, motion_data)[0][1]
            max_value = max(cov_array)
            max_index = cov_array.index(max_value)
            twolargest = heapq.nlargest(2, cov_array)
            #print max_value
            if ((max_value > 0.9) and (abs(twolargest[0] - twolargest[1]) > 0.3)):
                name = self.table.regTable[DEF_MACADDR[max_index]]
                if (name == " "):
                    return
                self.table.unpair(DEF_MACADDR[max_index])
                self.sock2.sendto(str(self.table.regTable), (self.IP_presentation, self.PORT_to_presentation))
                tkMessageBox.showinfo('confirmation', '%s is unpaired with %s' % (name, DEF_MACADDR[max_index]))

    def pop_window(self, name):
        self.window = tk.Toplevel(self.master)
        self.app = reg_UI2(self.window, name)

    def create_battery_table(self, battery_table):
        self.window = tk.Toplevel(self.master)
        self.battery_gui = battery_UI(self.window, battery_table)

    def update_battery_table(self, watch_id, battery_status, health_status):
        self.battery_gui.update(watch_id, battery_status, health_status)

## This class pop up a new window that confirm the registration information.
class reg_UI2:

    pair_status = False
    name = " "

    def __init__(self, master, name):
        reg_UI2.name = name
        self.master = master
        var = "You are registrating as " + name
        self.text = tk.Message(self.master, text=var, width=800)
        self.text.pack()
        self.confirm_button = tk.Button(self.master, text="confirm", width=20)
        self.confirm_button.pack()
        self.confirm_button.bind('<Button-1>', self.update_table)
        self.cancel_button = tk.Button(self.master, text="cancel", command=self.close_windows, width=20)
        self.cancel_button.pack()

    def close_windows(self):
        self.master.destroy()
        return

    def update_table(self, event):
        reg_UI2.pair_status = True
        self.master.destroy()
        return

class battery_UI:
    def __init__(self, master, battery_table):
        self.battery_table = battery_table
        self.master = master

        self.tree = ttk.Treeview(self.master, show="headings")
        self.tree["columns"] = ("one", "two", "three")
        self.tree.column("one", width=200, anchor='center')
        self.tree.column("two", width=200, anchor='center')
        self.tree.column("three", width=200, anchor='center')
        self.tree.heading("one", text="Watch ID")
        self.tree.heading("two", text="Battery Life Remaining")
        self.tree.heading("three", text="Health Status")
        for key, value in self.battery_table.iteritems():
            self.tree.insert('','end', (key, value[0], value[1]))

    def update(self, watch_id, battery_status, health_status):
        index = self.battery_table.keys().index(watch_id)
        item = self.tree.get_children()
        self.tree.set(item[index], ('one', 'two', 'three'), (watch_id, battery_status, health_status))

class ThreadedClient:

    def __init__(self, master):
        self.name_list = ["Jian", "William", "Peiming", "Viswam", "Bassem", "Ali A", "Xien", "Ning", "Kim", "Zach"]
        self.master = master
        self.watch_queue = [collections.deque(maxlen=100) for x in range(WATCH_NUM)]
        self.motion_queue = collections.deque(maxlen=100)
        self.gui = reg_UI(master, self.name_list, self.motion_queue, self.watch_queue)

        # Start smart watch server and start to receive data from all clients.
        UDP_IP = '192.168.0.120'
        UDP_PORT = 4570
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((UDP_IP, UDP_PORT))
        thread.start_new_thread(self.read_watch, ())


        # Start to receive data from MotionNet.
        self.serial = serial.Serial("COM6", 115200, timeout=5)
        self.data = [0 for x in range(50)]
        self.data_package = Queue.Queue(maxsize=50)
        self.parsed_data = [0 for x in range(6)]
        thread.start_new_thread(self.read_motion, ())
        self.lock = thread.allocate_lock()
        self.periodicCall()

    def periodicCall(self):
        self.gui.processIncoming()
        self.master.after(50, self.periodicCall)

    def read_watch(self):
        while True:
            # packet format: str(device_id + " " + packet_type +  " " + gyro_mag)
            data, addr = self.sock.recvfrom(1024)
            #print data
            parsed_data = data.split(' ')
            if (parsed_data[1] == 'w'):
                gyro_mag = float(parsed_data[2])
                for i in range(WATCH_NUM):
                    if (parsed_data[0] == DEF_MACADDR[i]):
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


