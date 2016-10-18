import ttk

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

    def update(self, watch_id, health_status):
        index = self.battery_table.keys().index(watch_id)
        item = self.tree.get_children()
        self.tree.set(item[index], 'three', health_status)