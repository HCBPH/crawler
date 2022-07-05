from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from prettytable import PrettyTable

ap_date = ["2022-07-07", "2022-07-10"]
# 在此设置出发、到达城市 需要从携程查看相应城市代码
depart_city = "SHA"
arrive_city = "BJS"
# 在此设置机票阈值
expect_price = 1000

options = webdriver.ChromeOptions()
# options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-gpu')
options.add_argument('--disable-dev-shm-usage')
browser = webdriver.Chrome("/work/driver/chromedriver", options=options)

js_down = "var q=document.documentElement.scrollTop=10000"
js_top = "var q=document.documentElement.scrollTop=0"
airplane_table = PrettyTable(["航空公司", "航班号", "机型", "大小", "出发时间", "到达时间", "出发地", "目的地", "优惠",
                              "价格", "到达准点率", "出发准点率", "平均延误", "平均提前", "devices", "舱位"])

for yd_date in ap_date:
    t1 = time.time()
    print(f'[{time.strftime("%Y-%m-%d %H:%M:%S")}]:正在爬取{yd_date}的机票')
    h = ['----------------' for i in range(7)]
    h.append(yd_date)
    h.extend(['-----------' for i in range(8)])
    airplane_table.add_row(h)

    browser.get(f"https://flights.ctrip.com/online/list/oneway-{depart_city}-{arrive_city}?_=1&depdate={yd_date}")

    browser.implicitly_wait(10)

    browser.execute_script(js_down)  # 滚动网页 使得数据加载完毕
    time.sleep(1)
    browser.execute_script(js_down)
    time.sleep(1)
    # browser.execute_script(js_top)
    browser.execute_script(js_down)
    time.sleep(1)
    browser.execute_script(js_down)
    time.sleep(1)
    browser.execute_script(js_down)
    time.sleep(1)
    browser.execute_script(js_down)
    time.sleep(1)

    flight_airlines = browser.find_elements(By.CLASS_NAME, 'flight-airline')
    flight_details = browser.find_elements(By.CLASS_NAME, 'flight-detail')
    flight_tags = browser.find_elements(By.CLASS_NAME, 'flight-tags')
    flight_prices = browser.find_elements(By.CLASS_NAME, 'flight-price')
    comfort_details = browser.find_elements(By.CLASS_NAME, 'comfort-detail')

    print(len(flight_airlines))
    print(len(flight_details))
    print(len(flight_tags))
    print(len(flight_prices))
    print(len(comfort_details))

    for i, (flight_airline, flight_detail, flight_tag, flight_price) in enumerate(
            zip(flight_airlines,  flight_details, flight_tags, flight_prices)):
        print(flight_airline)
        print(flight_detail)
        print(flight_tag)
        print(flight_price)
        # airlines, tmp = flight_airline.text.split("\n")
        # plane_no, plane_type = tmp.split(" ")
        # is_big = 0
        # if "中" in plane_type or "窄" in plane_type:
        #     is_big = 1
        # elif "大" in plane_type or "宽" in plane_type:
        #     is_big = 2
        # flight_detail_text = flight_detail.get_attribute('innerText')
        # flight_airline = flight_airline.get_attribute('innerText').split('\n')
        # try:  # 经停航班会有更多的返回值 不考虑经停航班
        #     plane_dt, plane_dl, plane_at, plane_al = flight_detail.text.split("\n")
        # except:
        #     continue
        # tag = flight_tag.get_attribute('innerText')
        # price = flight_price.get_attribute('innerText').split('\n')[0][1:-1]
        # delay_rate = delay_rate.get_attribute('innerText')
        # device = device.get_attribute('innerText')
        # airplane_table.add_row([airlines, plane_no, plane_type, is_big, plane_dt, plane_dl, plane_at, plane_al, tag, price, delay_rate, delay_rate, delay_rate, delay_rate,
        #                         device])
    time.sleep(3)
    # with open(f"/work/xiecheng/res/{time.time()}.html", "wb") as f:
    #     f.write(browser.page_source.encode("utf8", 'ignore'))
    print(f'[{time.strftime("%Y-%m-%d %H:%M:%S")}]:{yd_date}爬取完成，耗时{time.time() - t1}s')
print(airplane_table)

data_html = airplane_table.get_html_string()
# send_mail(data_html)
browser.close()
# os.system('taskkill /im edgedriver.exe /F')
