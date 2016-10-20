import ttk
import Tkinter as tk
import thread

class battery_UI:
    def __init__(self, master, battery_table):
        self.battery_table = battery_table
        self.master = master
        master.title("Battery Health Status")
        self.tree = ttk.Treeview(self.master, show="headings")
        self.tree["columns"] = ("one", "two", "three")
        self.tree.column("one", width=200, anchor='center')
        self.tree.column("two", width=200, anchor='center')
        self.tree.column("three", width=200, anchor='center')
        self.tree.heading("one", text="Watch ID")
        self.tree.heading("two", text="Battery Life Remaining")
        self.tree.heading("three", text="Health Status")
        self.tree.pack()
        self.lock = thread.allocate_lock()
        for key, value in self.battery_table.iteritems():
            self.tree.insert('','end', values=(key, value[0], value[1]))


    def update_status(self, watch_id, battery_status, health_status):
        index = self.battery_table.keys().index(watch_id)
        self.lock.acquire()
        item = self.tree.get_children()
        self.tree.set(item[index], column="two", value=battery_status)
        self.tree.set(item[index], column="three", value=health_status)
        self.lock.release()

    def update_health(self, watch_id, health_status):
        index = self.battery_table.keys().index(watch_id)
        self.lock.acquire()
        item = self.tree.get_children()
        self.tree.set(item[index], column="three", value=health_status)
        self.lock.release()

    def close_windows(self):
        self.master.destroy()
        return
