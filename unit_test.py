##encoding=utf8

from __future__ import print_function
from pyestate.trulia import Trulia
from pyestate.lib.logger import Log
from selenium import webdriver

log = Log()

class Trulia_UT(object):
    @staticmethod
    def property_detail():
        log = Log()
        driver = webdriver.Firefox()
        driver.set_page_load_timeout(30) # 设置timeout时间为30秒
        trulia = Trulia(log)
        trulia.add_driver(driver)
        
        query = [("3119 Terrace St", "15213"),
                 ("11942 Glen Alden Rd", "22030"),
                 ("2343 23rd Ave S", "98144"),
                 ("955 26th St NW APT 412", "20037"),
                 ("2206 Boxwood Dr", "95128"),
                 ("738 Duncan St", "94131"),
                 ("1109 Folsom Ave", "98902"),
                 ("1911 Greyson Dr", "78664"),
                 ("1611 S Cleveland St", "72204"),
                 ("320 Lacrosse Dr", "60440"),
                 ("1125 Commonwealth Ave APT 14", "02134"),]
        
        for street, zipcode in query:
            try:
                print("anlysising %s, %s" % (street, zipcode))
                print(trulia.stable_crawler(street, zipcode))
                print("SUCCESS!")
            except Exception as e:
                log.write(str(e), "%s %s" % (street, zipcode) )
        print("Complete")
        
if __name__ == "__main__":
    Trulia_UT.property_detail()

    pass