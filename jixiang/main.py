import time
import datetime
import random

from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from airline import Airline
import pymysql
from prettytable import PrettyTable

from selenium import webdriver
import string
import zipfile


def create_proxy_auth_extension(proxy_host, proxy_port,
                                proxy_username, proxy_password,
                                scheme='http', plugin_path=None):
    if plugin_path is None:
        plugin_path = r'./proxy_auth_plugin.zip'
    manifest_json = """
        {
            "version": "1.0.0",
            "manifest_version": 2,
            "name": "Abuyun Proxy",
            "permissions": [
                "proxy",
                "tabs",
                "unlimitedStorage",
                "storage",
                "<all_urls>",
                "webRequest",
                "webRequestBlocking"
            ],
            "background": {
                "scripts": ["background.js"]
            },
            "minimum_chrome_version":"22.0.0"
        }
        """

    background_js = string.Template(
        """
        var config = {
            mode: "fixed_servers",
            rules: {
                singleProxy: {
                    scheme: "${scheme}",
                    host: "${host}",
                    port: parseInt(${port})
                },
                bypassList: ["foobar.com"]
            }
          };

        chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

        function callbackFn(details) {
            return {
                authCredentials: {
                    username: "${username}",
                    password: "${password}"
                }
            };
        }

        chrome.webRequest.onAuthRequired.addListener(
            callbackFn,
            {urls: ["<all_urls>"]},
            ['blocking']
        );
        """
    ).substitute(
        host=proxy_host,
        port=proxy_port,
        username=proxy_username,
        password=proxy_password,
        scheme=scheme,
    )

    with zipfile.ZipFile(plugin_path, 'w') as zp:
        zp.writestr("manifest.json", manifest_json)
        zp.writestr("background.js", background_js)

    return plugin_path


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


with open("proxies", 'r') as f:
    proxies = f.read().split(" ")

# 代理服务器
proxyHost = "http-short.xiaoxiangdaili.com"
proxyPort = "10010"

# 代理隧道验证信息
proxyUser = "861312288987435008"
proxyPass = "KxJtjQlG"

proxy_auth_plugin_path = create_proxy_auth_extension(
    proxy_host=proxyHost,
    proxy_port=proxyPort,
    proxy_username=proxyUser,
    proxy_password=proxyPass)

# selenium设置
options = webdriver.ChromeOptions()
# options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument("--window-size=4000, 4000")
options.add_argument('--disable-gpu')
options.add_argument('--disable-dev-shm-usage')
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument("--start-maximized")
options.add_extension(proxy_auth_plugin_path)
# options.add_argument("--proxy-server=http://http-dynamic-S03.xiaoxiangdaili.com")

driver = webdriver.Chrome(r"D:\project\crawler\chromedriver.exe", options=options)
# webdriver.DesiredCapabilities.CHROME['proxy'] = {
#     "httpProxy": '121.201.49.231',
#     "sslProxy": '121.201.49.231	',
#     "proxyType": "MANUAL",
#     "username": "530590767",
#     "password": "ycj123456"
# }

driver.implicitly_wait(3)

driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    "source": """
    Object.defineProperty(navigator, 'webdriver', {
      get: () => undefined
    })
  """
})
driver.execute_cdp_cmd("Network.enable", {})
driver.execute_cdp_cmd("Network.setExtraHTTPHeaders", {"headers": {"User-Agent": "browser1"}})

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
city_list = ["北京", "广州", "深圳", "成都", "杭州", "武汉", "西安", "重庆", "长沙", "青岛",
             "南京", "厦门", "昆明", "大连", "天津", "郑州", "三亚", "济南", "福州"]

# with open("/work/xiamen/proxies", "r") as f:
#     proxy_list = f.readlines()

date_start = "2022-07-17"
date_end = "2022-08-08"

city_frequency = 6
date_frequency = 1
out_count = 0
count = 0
i = 0
t_start = time.time()
for date in generate_date_list(date_start, date_end):
    # ————————————————————————————————爬取某一天上海到所有城市start————————————————————————————
    while i < len(city_list):
        city = city_list[i]
        i += 1
        # ————————————————————————————————某天某地所有航班start————————————————————————————————
        t_start0 = time.time()
        try:
            url = f"http://www.juneyaoair.com/pages/Flight/flight.aspx?flightType=OW&sendCity=上海&sendCode=SHA&arrCity={city}&arrCode=CTU&directType=N&tripType=D&departureDate={date}&returnDate={date}"
            driver.get(url)
            time.sleep(1)
            printf(f"正在爬取:上海-->{city}:{date}")
            h = ['----------------' for i in range(7)]
            h.append(f"上海-->{city}:{date}")
            h.extend(['-----------' for i in range(8)])
            airline_table.add_row(h)

            try:
                btn_known = driver.find_element_by_xpath('/html/body/div[19]/div[3]/span')
                ActionChains(driver).move_to_element(btn_known).click().click().perform()
                clickables = driver.find_elements_by_xpath(
                    "/html/body/div[1]/div[5]/div[1]/div[1]/div[2]/table/tbody/tr[@class='flt_more']/td/div/a")
                for clickable in clickables:
                    ActionChains(driver).move_to_element(clickable).click().perform()
                table = driver.find_element_by_xpath('//*[@id="flt_hd_table"]/table/tbody')
            except Exception as e:
                if out_count > 3:
                    with open("./error.log", 'w') as f:
                        f.write(f"table error:{e}")
                else:
                    i -= 1
                    out_count += 1
                continue

            airline = None
            trs = table.find_elements_by_xpath("./tr")
            if len(trs) < 2:
                printf(f"查询无结果:上海-->{city}:{date},耗时：{time.time() - t_start0}")
                if out_count > 5:
                    with open("./warning.log", 'w') as f:
                        f.write(f"查询无结果:上海-->{city}:{date}")
                else:
                    i -= 1
                    out_count += 1
                continue
            for tr in trs:
                # ————————————————————————————————解析每张机票start——————————————————————————————————————
                if tr.get_attribute("class") == "title":
                    al_num = tr.find_elements_by_class_name("flt_No")[0].text
                    al_type = tr.find_elements_by_class_name("flt_showTypeInfo")[0].text
                    ls_t = al_type.strip("）").split("（")
                    if len(ls_t) == 2:
                        al_type, al_size = ls_t
                    elif len(ls_t) == 1:
                        al_type = ls_t[0]
                        al_size = ""
                    else:
                        al_type = ""
                        al_size = ""

                    t = tr.find_elements_by_class_name("flt_date")
                    p = tr.find_elements_by_class_name("flt_site")
                    departure_time = date + " " + t[0].text + ":00"
                    arrival_time = date + " " + t[1].text + ":00"
                    departure_place = p[0].text
                    arrival_place = p[1].text
                    airline = Airline(al_num, "吉祥航空", al_type, al_size, departure_time, arrival_time,
                                      "上海", city)
                elif tr.get_attribute("class") == "cnt":
                    cabin = tr.find_element_by_xpath("./td[1]").text
                    cabin = cabin.split(' ')[0]
                    cabin, promotion = cabin.strip(")").split("(")
                    if cabin == "经济舱":
                        cabin = 1
                    elif cabin == "公务舱":
                        cabin = 2
                    elif cabin == "头等舱":
                        cabin = 3
                    else:
                        with open("./warning.log", "w") as f:
                            f.write("unexpected cabin type:", cabin)
                    devices = tr.find_element_by_xpath('./td[3]/span').text
                    price = tr.find_element_by_xpath('./td[7]/div/div/span').text
                    promotion += ("," + tr.find_element_by_xpath('./td[9]').text)
                    airline.cabin = cabin
                    airline.price = price
                    airline.promotion = promotion
                    airline.devices = devices
                    cursor.execute(
                        "insert into airline_ticket(creater, airline, al_num, al_type, al_size, departure_time, arrival_time, departure_place, arrival_place, promotion, price, departure_rate, arrival_rate, delay_time, advance_time, devices, cabin) "
                        "values('ycj', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}');".format(
                            *airline.features()))
                    airline_table.add_row(airline.features())
                    count += 1
            # ————————————————————————————————解析每张机票end——————————————————————————————————————
        except Exception as e:
            with open("./error.log", "w") as f:
                f.write(str(e))
                f.write(tr.text)
                printf(f"已爬取{count}张机票,error:", e)
        db.commit()
        if (time.time() - t_start0) <= city_frequency:
            time.sleep(int(city_frequency + 1 - (time.time() - t_start0)))
        printf(f"爬取完成:上海-->{city}:{date},耗时：{time.time() - t_start0}")

        # ————————————————————————————————某天某地所有航班end———————————————————————————————————————
    i = 0
    time.sleep(date_frequency)
    # ————————————————————————————————爬取某一天上海到所有城市end————————————————————————————————————
print(f"总共爬取{count}张机票，耗时{time.time() - t_start}s")
print(airline_table)
driver.quit()
driver.close()
cursor.close()
db.close()
