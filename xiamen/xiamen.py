import requests
import json
import time
import pymysql
from prettytable import PrettyTable
import datetime
import random


def generate_date_list(start, end):
    ret = []
    if isinstance(start, str):
        start = datetime.datetime.strptime(start, "%Y-%m-%d")
    if isinstance(end, str):
        end = datetime.datetime.strptime(end, "%Y-%m-%d")
    if start > end:
        tmp = start
        start = end
        end = tmp
    diff = end - start  # datetime.timedelta(12)

    ret.append(start.strftime("%Y-%m-%d"))
    for i in range(diff.days):
        ret.append((start + datetime.timedelta(i + 1)).strftime("%Y-%m-%d"))
    return ret


def printf(*s):
    print(f'>>>[{time.strftime("%Y-%m-%d %H:%M:%S")}] ', *s)


def post(header, payload):
    proxy = random.choice(proxy_list).strip()
    printf(f"使用代理:{proxy}")
    # proxies = {
    #     "http": "http://530590767:ycj256983@" + proxy,
    #     "https": "http://530590767:ycj256983@" + proxy
    # }
    proxies = {
        "http": "http://t15666346852551:ycj123456@" + proxy,
        "https": "http://t15666346852551:ycj123456@" + proxy
    }
    try:
        r = requests.post(
                "https://mobileapi.xiamenair.com/mobile-starter/api/v5/Offer/shopping?preBusiness=0&type=D",
                headers=header, json=payload, proxies=proxies, auth=("530590767", "ycj256983"), timeout=5)
        with open("proxies_alive", "w") as f:
            f.write(proxy+"\n")
        return r
    except Exception as e:
        printf("发现失效代理:", proxy)
        return post(header, payload)




# mysql
db = pymysql.connect(
    host="1.117.74.41",
    user="xiecheng",
    password="xiecheng",
    database="xiecheng",
    charset="utf8"
)
cursor = db.cursor()

# 输出
airline_table = PrettyTable(["航空公司", "航班号", "机型", "大小", "出发时间", "到达时间", "出发地", "目的地", "优惠",
                             "价格", "出发准点率", "到达准点率", "平均延误", "平均提前", "设施及服务", "舱位"])

# 爬虫参数
with open("/work/xiamen/city_code.json", "r") as f:
    city_code = json.load(f)

with open("/work/xiamen/proxies", "r") as f:
    proxy_list = f.readlines()

header = {
    "user-agent": "Mozilla/5.0 (Linux; U; Android 4.0.2; en-us; Galaxy Nexus Build/ICL53F) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30",
}

with open("/work/xiamen/payload.json", "r") as f:
    payload = json.load(f)

date_start = "2022-07-25"
date_end = "2022-08-08"

for date in generate_date_list(date_start, date_end):
    # ——————————————————————————————————————爬取某天航班start—————————————————————————————————————————————————————————————
    t_start = time.time()
    for departure_code in ["PVG", "SHA"]:
        for name, arrival_codes in city_code.items():
            for arrival_code in list(arrival_codes):
                try:
                    printf(f"正在爬取:上海({departure_code})-->{name}({arrival_code}):{date}")
                    h = ['----------------' for i in range(7)]
                    h.append(date)
                    h.extend(['-----------' for i in range(8)])
                    airline_table.add_row(h)
                    payload['itineraries'][0]['departureDate'] = date
                    payload['itineraries'][0]['origin']['airport']['code'] = departure_code
                    payload['itineraries'][0]['destination']['airport']['code'] = arrival_code

                    response = post(header, payload)

                    data = response.json()['data']['odData']
                    # —————————————————————————————————————爬取定时定地点所有航班start—————————————————————————————————————
                    for i in data[list(data.keys())[0]]:
                        segments = i['segments']
                        segments = segments[list(segments.keys())[0]][0]
                        # print(segments)
                        offers = i['offers']['[ADT1]']

                        airline = "厦门航空"
                        al_num = segments['marketingCarrier']['carrier']['code'] + segments['marketingCarrier'][
                            'flightNumber']
                        al_type = segments['equipment']['name'] + segments['equipment']['code']
                        al_size = ""
                        departure_time = segments['departure']['aircraftScheduledDateTime'].replace('T', ' ')
                        arrival_time = segments['arrival']['aircraftScheduledDateTime'].replace('T', ' ')
                        departure_place = segments['departure']["iataLocationName"]
                        arrival_place = segments['arrival']["iataLocationName"]
                        promotion = ""
                        departure_rate = ""
                        arrival_rate = ""
                        delay_time = ""
                        advance_time = ""
                        devices = ""

                        for ticket in offers:
                            cabin_t = ticket["cabinType"]
                            if "economy" in cabin_t.lower() or "经济" in cabin_t:
                                cabin = 1
                            elif "business" in cabin_t.lower() or "商务" in cabin_t:
                                cabin = 2
                            elif "first" in cabin_t.lower() or "头等" in cabin_t:
                                cabin = 3
                            else:
                                cabin = 0

                            price = ticket['baseAmount']
                            cursor.execute(
                                "insert into airline_ticket(creater, airline, al_num, al_type, al_size, departure_time, arrival_time, departure_place, arrival_place, promotion, price, departure_rate, arrival_rate, delay_time, advance_time, devices, cabin) "
                                "values('ycj', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}');".format(
                                    airline, al_num, al_type,
                                    al_size, departure_time, arrival_time,
                                    departure_place, arrival_place,
                                    promotion, price,
                                    departure_rate, arrival_rate,
                                    delay_time, advance_time,
                                    devices, cabin))

                            airline_table.add_row([airline, al_num, al_type,
                                                   al_size, departure_time, arrival_time,
                                                   departure_place, arrival_place,
                                                   promotion, price,
                                                   departure_rate, arrival_rate,
                                                   delay_time, advance_time,
                                                   devices, cabin])
                            db.commit()
                    # —————————————————————————————————————爬取定时定地点所有航班结束—————————————————————————————————————
                except Exception as e:
                    printf(f"something error when crawling:上海-->{name}:{date}")
                    print(e)
    printf(f"爬取完成:上海-->{name}:{date},耗时：{time.time() - t_start}")
    # ——————————————————————————————————————爬取某天航班end———————————————————————————————————————————————————————————————
print(airline_table)
cursor.close()
db.close()
