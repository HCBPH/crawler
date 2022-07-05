from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time
import datetime
from prettytable import PrettyTable
from airline import Airline
import os
import pymysql


def printf(*s):
    print(f'>>>[{time.strftime("%Y-%m-%d %H:%M:%S")}] ', *s)

def generate_date_list(start, end):
    ret = []
    if isinstance(start, str):
        start = datetime.datetime.strptime(start, "%Y-%m-%d")
    if isinstance(end, str):
        end = datetime.datetime.strptime(end, "%Y-%m-%d")
    if start > end:
        tmp = start
        start = end
        end = t
    diff = end - start  # datetime.timedelta(12)

    ret.append(start.strftime("%Y-%m-%d"))
    for i in range(diff.days):
        ret.append((start + datetime.timedelta(1)).strftime("%Y-%m-%d"))
    return ret


db = pymysql.connect(
    host="localhost",
    user="ycj",
    password="000000",
    database="xiecheng",
    charset="utf8"
)
cursor = db.cursor()

with open("./proxies", "r") as f:
    proxies = f.readlines()


start = "2022-6-29"
end = "2022-7-10"
depart_city = "SHA"
arrive_city = "BJS"
pages = 1
page_per_time = 1

options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument("--window-size=10000,10000")
options.add_argument('--disable-gpu')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('user-agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"')
# options.add_argument('cookie="MKT_CKID=1655811637254.dubey.k0o6; GUID=09031036218372901773; _RGUID=0ef850db-d62b-429e-bf67-e99e0db385cf; _RDG=2861b8e50e22ee28bb2f1b092914544be8; _RSG=UAqAMlDKux0FNuiDuPwdzB; MKT_Pagesource=PC; _bfaStatusPVSend=1; _gcl_aw=GCL.1655881791.EAIaIQobChMIiP3SqsDA-AIVIcLCBB1CugQjEAAYASAAEgIa4fD_BwE; _gcl_dc=GCL.1655881791.EAIaIQobChMIiP3SqsDA-AIVIcLCBB1CugQjEAAYASAAEgIa4fD_BwE; appFloatCnt=2; nfes_isSupportWebP=1; nfes_isSupportWebP=1; _abtest_userid=b8e50f32-f905-46c4-b565-55659683576f; login_uid=3C267777E1B3658EB489419DA69F9711; login_type=0; cticket=363DC66F7A1E51D62067BD8160CC504277C0032A7962B54AD5C9439C45279F2F; AHeadUserInfo=VipGrade=0&VipGradeName=%C6%D5%CD%A8%BB%E1%D4%B1&UserName=&NoReadMessageCount=0; DUID=u=3C267777E1B3658EB489419DA69F9711&v=0; IsNonUser=F; IsPersonalizedLogin=F; UUID=9A5E626C2D834EA09DB0B06F6CF9D29C; _RF1=114.83.38.117; Union=OUID=index&AllianceID=4897&SID=155952&SourceID=&createtime=1656307148&Expires=1656911947677; MKT_OrderClick=ASID=4897155952&AID=4897&CSID=155952&OUID=index&CT=1656307147679&CURL=https%3A%2F%2Fwww.ctrip.com%2F%3Fsid%3D155952%26allianceid%3D4897%26ouid%3Dindex&VAL={"pc_vid":"1655811636870.1brxrc"}; MKT_CKID_LMT=1656307147824; __zpspc=9.5.1656307147.1656307147.1%232%7Cwww.baidu.com%7C%7C%7C%25E6%2590%25BA%25E7%25A8%258B%7C%23; _jzqco=%7C%7C%7C%7C1656307147899%7C1.1180683648.1655811637211.1656034847303.1656307147830.1656034847303.1656307147830.0.0.0.9.9; FlightIntl=Search=[%22SHA|%E4%B8%8A%E6%B5%B7(SHA)|2|SHA|480%22%2C%22BJS|%E5%8C%97%E4%BA%AC(BJS)|1|BJS|480%22%2C%222022-07-09%22]; _bfi=p1%3D10320673302%26p2%3D10320673302%26v1%3D86%26v2%3D85; _bfaStatus=success; _bfa=1.1655811636870.1brxrc.1.1656094132473.1656307147364.8.87.1; _bfs=1.5; _ubtstatus=%7B%22vid%22%3A%221655811636870.1brxrc%22%2C%22sid%22%3A8%2C%22pvid%22%3A87%2C%22pid%22%3A10320673302%7D"')
# 20.81.62.32
browser = webdriver.Chrome("/work/driver/chromedriver", options=options)
js_down = "var q=document.documentElement.scrollTop=10000"
js_top = "var q=document.documentElement.scrollTop=0"

airplane_table = PrettyTable(["航空公司", "航班号", "机型", "大小", "出发时间", "到达时间", "出发地", "目的地", "优惠",
                              "价格", "出发准点率", "到达准点率", "平均延误", "平均提前", "devices", "舱位"])

for yd_date in generate_date_list(start, end):
    t1 = time.time()
    printf('正在爬取' + yd_date + '的机票')
    h = ['----------------' for i in range(7)]
    h.append(yd_date)
    h.extend(['-----------' for i in range(8)])
    airplane_table.add_row(h)

    browser.get(f"https://flights.ctrip.com/online/list/oneway-{depart_city}-{arrive_city}?_=1&depdate={yd_date}")

    browser.implicitly_wait(10)

    for i in range(pages):
        progress = int((i+1) / pages * 100)
        print(f"\rscrolling process:[{'>' * progress}{' ' * int(100 - progress)}] {progress}%", end='')
        browser.execute_script(js_down)  # 滚动网页 使得数据加载完毕
        time.sleep(page_per_time)
    print()
    time.sleep(5)

    flight_boxes = browser.find_elements(By.CLASS_NAME, "flight-box")
    # comfort_details = browser.find_elements(By.CLASS_NAME, "comfort-detail")

    num_flight_boxes = len(flight_boxes)
    # num_comfort_details = len(comfort_details)
    printf("flight counts:" + str(num_flight_boxes))
    # printf("comfort details counts:" + str(num_comfort_details))

    airlines = {}
    for i, flight_box in enumerate(flight_boxes):
        progress = int((i+1) / num_flight_boxes * 100)
        print(f"\rcrawling process:[{'>' * progress}{' ' * int(100 - progress)}] {progress}%", end='')
        flag = 0
        airline = Airline()
        sp = flight_box.text.split("\n")

        try:
            # 移动到comfort-detail元素，让他显示出来，才能进行爬取
            # ActionChains(browser).move_to_element(
            #     flight_box.find_elements(By.CLASS_NAME, 'plane')[0]).click_and_hold().perform()

            # 1.
            airline.name = sp[0]

            # 2. 3.
            if sp[1] == "当日低价":
                airline.number, airline.type = [None, None]
            elif ":" in sp[1]:
                flag -= 1
                airline.number, airline.type = [None, None]
            else:
                airline.number, airline.type = sp[1].split(" ")[0:2]
                # 4.
                if "中" in airline.type or "窄" in airline.type:
                    airline.isBig = 1
                if "大" in airline.type or "宽" in airline.type:
                    airline.isBig = 2

            # 5. 6. 7. 8.
            t = sp[2 + flag]
            while ':' not in t:
                flag += 1
                t = sp[2 + flag]
            airline.dep_time = sp[2 + flag]
            airline.dep_place = sp[3 + flag]
            airline.ach_time = sp[4 + flag]
            if "天" in sp[5 + flag]:
                flag += 1
            airline.ach_place = sp[5 + flag]

            # 9.
            airline.promotion = 1 if ("折" in sp[-4] or "减" in sp[-4]) else 0

            # 10.
            airline.price = sp[-3].strip("起").strip("¥")

            # 11.
            # comfort_detail = browser.find_elements(By.CLASS_NAME, "comfort-detail")

            airlines[airline.number] = airline
        except:
            print()
            printf("出错记录:", sp, "\n")
            continue
        # -------for end-------
    print()

    # 将数据插入到可视化组建
    for k, v in airlines.items():
        airplane_table.add_row(v.features())
        sql = "insert into airline_ticket_crawler(airline,al_num,al_type,al_size,departure_time,arrival_time,departure_place,arrival_place,promotion,price,departure_rate,arrival_rate,delay_time,advance_time,devices,cabin) " \
              "values('{0[0]}','{0[1]}','{0[2]}','{0[3]}','{0[4]}','{0[5]}','{0[6]}','{0[7]}','{0[8]}','{0[9]}','{0[10]}','{0[11]}','{0[12]}','{0[13]}','{0[14]}','{0[15]}')".format(v.features())
        cursor.execute(sql)
    db.commit()

    if not os.path.exists("/work/xiecheng/res"):
        os.makedirs("/work/xiecheng/res")
    with open(f"/work/xiecheng/res/{time.time()}.html", "wb") as f:
        f.write(browser.page_source.encode("utf8", 'ignore'))
    time.sleep(2)
    printf(f'{yd_date}爬取完成，耗时{time.time() - t1}s')

print(airplane_table)

data_html = airplane_table.get_html_string()
# send_mail(data_html)
cursor.close()
db.close()
browser.close()
# os.system('taskkill /im edgedriver.exe /F')
