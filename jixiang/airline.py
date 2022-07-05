class Airline:

    def __init__(self, al_num, airline: str = "吉祥航空", al_type="", al_size="",
                 departure_time="", arrival_time="", departure_place="", arrival_place="",
                 ):
        self.airline = airline
        self.al_num = al_num
        self.al_type = al_type
        self.al_size = al_size
        self.departure_time = departure_time
        self.arrival_time = arrival_time
        self.departure_place = departure_place
        self.arrival_place = arrival_place
        self.promotion = ""
        self.price = ""
        self.departure_rate = ""
        self.arrival_rate = ""
        self.delay_time = ""
        self.advance_time = ""
        self.devices = ""
        self.cabin = ""

    def features(self):
        return [str(i) for i in[
            self.airline,
            self.al_num,
            self.al_type,
            self.al_size,
            self.departure_time,
            self.arrival_time,
            self.departure_place,
            self.arrival_place,
            self.promotion,
            self.price,
            self.departure_rate,
            self.arrival_rate,
            self.delay_time,
            self.advance_time,
            self.devices,
            self.cabin,
        ]]

    def print(self):
        print("\t".join(["航空公司", "航班号", "机型", "机型大小", "出发时间", "到达时间", "出发地", "目的地", "优惠",
                         "价格", "到达准点率", "出发准点率", "平均延误", "平均提前", "服务", "舱位"]))
        print("\t".join(self.features()))
