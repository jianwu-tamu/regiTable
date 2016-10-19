import Tkinter as tk
from RegTable import RegTable
from functools import partial
import tkMessageBox
import thread
import socket
import numpy
import heapq
from reg_UI2 import reg_UI2
from battery_UI import battery_UI

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
        self.IP_presentation = '192.168.0.109'
        self.PORT_to_presentation = 4564
        self.sock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.battery_table = {}
        for i in range(len(DEF_MACADDR)):
            self.battery_table[DEF_MACADDR[i]] = ("99%", "yes")
        print self.battery_table

        self.create_battery_table(self.battery_table)


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
                if (len(watch_gyro[i]) == 100 and len(MotionNet_gyro) == 100):
                    watch_data = list(watch_gyro[i])
                    motion_data = list(MotionNet_gyro)
                    cov_array[i] = numpy.corrcoef(watch_data, motion_data)[0][1]
            max_value = max(cov_array)
            max_index = cov_array.index(max_value)
            twolargest = heapq.nlargest(2, cov_array)
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

    def update_battery_table(self, watch_id, health_status):
        self.battery_gui.update(watch_id, health_status)