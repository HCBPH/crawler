class Airline:

    def __init__(self):
        self.name = ""
        self.number = None
        self.type = ""
        self.isBig = 0  # 0小型 1中型 2大型
        self.dep_time = ""
        self.ach_time = ""
        self.dep_place = ""
        self.ach_place = ""
        self.promotion = 0  # 促销
        self.price = 0
        self.dep_delay = 0  # 起飞的准时率
        self.ach_delay = 0  # 到达的准时率
        self.dep_dtime = 0  # 起飞的平均延迟时间
        self.ach_dtime = 0  # 到达的平均提前时间
        self.device = ""  # 飞机的配备，有无餐食、电影、插座等等
        self.cabin = "经济舱"

    def features(self):
        return [
            self.name, self.number, self.type, self.isBig, self.dep_time, self.ach_time,
            self.dep_place, self.ach_place, self.promotion, self.price,
            self.dep_delay, self.ach_delay, self.dep_dtime,
            self.ach_dtime, self.device, self.cabin
        ]

    def insert_db(self, cursor):
        pass

