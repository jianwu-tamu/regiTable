

class RegTable:
    def __init__(self, watch_number):
        self.watch_number = watch_number
        self.regTable = {}
        self.pair_status = {}

    def create_table(self, presenter_name, watch_name):
        assert(len(self.regTable) < self.watch_number)
        self.regTable[watch_name] = presenter_name
        print self.regTable
        print self.pair_status

    def update_table1(self, presenter_name, watch_name):
        assert(len(self.regTable) == self.watch_number)
        self.regTable[watch_name] = presenter_name
        print self.regTable

    def unpair(self, watch_name):
        self.regTable[watch_name] = " "
        print self.regTable