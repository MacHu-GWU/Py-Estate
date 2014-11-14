##encoding=utf8

from __future__ import print_function
from lib.misc import sleep
from lib.zillow import property_detail_by_street_and_zipcode, local_market
from lib.logger import Log
from bs4 import BeautifulSoup as BS4
from lib.js import load_js, dump_js
from itertools import cycle

log = Log()

class Zillow_UT(object):
    @staticmethod
    def property_detail():
        from selenium import webdriver
        query = [("955 26th St NW APT 412", "20037"),
                 ("3119 Terrace St", "15213"),
                 ("2206 Boxwood Dr", "95128"),
                 ("738 Duncan St", "94131"),
                 ("2343 23rd Ave S", "98144"),
                 ("1109 Folsom Ave", "98902"),
                 ("1911 Greyson Dr", "78664"),
                 ("1611 S Cleveland St", "72204"),
                 ("320 Lacrosse Dr", "60440"),
                 ("1125 Commonwealth Ave APT 14", "02134"),]
        
        driver = webdriver.Firefox()
        driver.set_page_load_timeout(30) # 设置timeout时间为30秒
        driver.get("http://www.zillow.com/") # 第一次人工登录zillow，手动输入验证码
        sleep(10)
        for street, zipcode in query:
            try:
                print("anlysising %s, %s" % (street, zipcode))
                res = property_detail_by_street_and_zipcode(driver, street, zipcode)
                print(res)
            except Exception as e:
                log.write(str(e), "%s %s" % (street, zipcode) )
            
        print("Complete")
        
    @staticmethod
    def local_stats():
        from selenium import webdriver
        import random
        state_list, zipcode_list = load_js(r"data\state_list.json"), load_js(r"data\zipcode_list.json")
        stats_by_state, stats_by_zipcode = load_js(r"stats_by_state.json"), load_js(r"stats_by_zipcode.json")
        random.shuffle(state_list)
        random.shuffle(zipcode_list)
        
        driver = webdriver.Firefox()
        driver.set_page_load_timeout(30) # 设置timeout时间为30秒
        driver.get("http://www.zillow.com/") # 第一次人工登录zillow，手动输入验证码
        sleep(10)
        
        saving_interval = 2
        cycler = cycle(list(range(saving_interval)))
        
        ### by states
        for state in state_list:
            if state not in stats_by_state:
                sleep(30)
                try: ## 每次爬之间睡眠30秒，防止被zillow检测出来
                    print("trying to analyze %s..." % state)
                    price, price_per_sqft, mid_sqft = local_market(driver, state)
                    stats_by_state[state] = (price, price_per_sqft, mid_sqft)
                    if next(cycler) == saving_interval - 1:
                        dump_js(stats_by_state, "stats_by_state.json", replace = True)
                except Exception as e:
                    log.write(str(e), "stats_%s" % state )
        dump_js(stats_by_state, "stats_by_state.json", replace = True)
        
        ### by zipcode
        for zipcode in zipcode_list:
            if zipcode not in stats_by_zipcode:
                sleep(30) ## 每次爬之间睡眠30秒，防止被zillow检测出来
                try:
                    print("trying to analyze %s..." % zipcode)
                    price, price_per_sqft, mid_sqft = local_market(driver, zipcode)
                    stats_by_zipcode[zipcode] = (price, price_per_sqft, mid_sqft)
                    if next(cycler) == saving_interval - 1:
                        dump_js(stats_by_zipcode, "stats_by_zipcode.json", replace = True)
                except Exception as e:
                    log.write(str(e), "stats_%s" % zipcode )
        dump_js(stats_by_zipcode, "stats_by_zipcode.json", replace = True)

        print("Complete")
        
if __name__ == "__main__":
#     Zillow_UT.property_detail()
    Zillow_UT.local_stats()